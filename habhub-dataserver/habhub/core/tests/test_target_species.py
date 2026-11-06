import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from habhub.core.models import TargetSpecies

pytestmark = pytest.mark.django_db


def make_species(**kwargs):
    # unsaved TargetSpecies, saving a new one doesn't start any data tasks
    return TargetSpecies(**dict({"species_id": "Test_species", "display_name": "Test species"}, **kwargs))


class TestSpeciesSubtype:
    def test_other_species_needs_a_subtype(self):
        species = make_species(species_type=TargetSpecies.OTHER)

        with pytest.raises(ValidationError) as error:
            species.full_clean()
        assert "species_subtype" in error.value.message_dict

    @pytest.mark.parametrize("subtype", ["Diatoms", "Dinoflagellates", "Ciliates", "Other"])
    def test_other_species_subtypes(self, subtype):
        make_species(species_type=TargetSpecies.OTHER, species_subtype=subtype).full_clean()

    def test_invalid_subtype(self):
        species = make_species(species_type=TargetSpecies.OTHER, species_subtype="Cyanobacteria")

        with pytest.raises(ValidationError):
            species.full_clean()

    def test_hab_species_cant_have_a_subtype(self):
        species = make_species(species_type=TargetSpecies.HAB, species_subtype=TargetSpecies.DIATOMS)

        with pytest.raises(ValidationError) as error:
            species.full_clean()
        assert "species_subtype" in error.value.message_dict

    def test_save_clears_subtype_for_hab_species(self):
        species = make_species(species_type=TargetSpecies.HAB, species_subtype=TargetSpecies.DIATOMS)
        species.save()

        species.refresh_from_db()
        assert species.species_subtype == ""

    def test_migration_set_existing_other_species(self):
        # the migrations add default TargetSpecies before the subtype field
        other = TargetSpecies.objects.filter(species_type=TargetSpecies.OTHER)
        assert all(species.species_subtype == "Other" for species in other)
        hab = TargetSpecies.objects.filter(species_type=TargetSpecies.HAB)
        assert all(species.species_subtype == "" for species in hab)

    def test_api_returns_subtype(self):
        make_species(species_type=TargetSpecies.OTHER, species_subtype=TargetSpecies.CILIATES).save()

        response = APIClient().get("/api/v1/core/target-species/")

        assert response.status_code == 200
        species = next(item for item in response.json() if item["id"] == "Test_species")
        assert species["speciesType"] == "Other"
        assert species["speciesSubtype"] == "Ciliates"
