from django.db import migrations, models


def set_other_subtype(apps, schema_editor):
    # existing Other species need a subtype, set "Other" until one is chosen in the admin
    TargetSpecies = apps.get_model("core", "TargetSpecies")
    TargetSpecies.objects.filter(species_type="Other").update(species_subtype="Other")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_alter_targetspecies_primary_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="targetspecies",
            name="species_subtype",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Diatoms", "Diatoms"),
                    ("Dinoflagellates", "Dinoflagellates"),
                    ("Ciliates", "Ciliates"),
                    ("Other", "Other"),
                ],
                help_text="Required for Other species, leave blank for HAB species",
                max_length=20,
            ),
        ),
        migrations.RunPython(set_other_subtype, migrations.RunPython.noop),
    ]
