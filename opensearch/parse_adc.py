# import IFCB utilities from https://github.com/joefutrelle/pyifcb package
from ifcb.data.adc import AdcFile
from ifcb.metrics.ml_analyzed import compute_ml_analyzed_adc

adc = AdcFile("D20230729T001110_IFCB110.adc")
print(adc)
ml_analyzed = compute_ml_analyzed_adc(adc)
print(ml_analyzed[0])
