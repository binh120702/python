from llm import gemini

model = gemini.Gemini()
labels_case_hinh_su = """PER	Person
ORG 	Organization
LOC	Location
DATE	Date, time, season
AMT	Amount of something
DOC_ID 	Document identifier
CRIMINAL	Criminal suspect
VICTIM	Victim
CRIME_TOOL	Crime tool
CRIME_LOCATION	Where did the crime happened?
CRIME_TIME	When did the crime happened?
COURT	Name of the court which has delivered the current judgement
STATUTE	Name of the act or law mentioned in the judgement
PROVISION	Sections, sub-sections, articles, orders, rules under a statute"""

labels_case_dan_su = """PER	Person
ORG 	Organization
LOC	Location
TIME	Date, time, season
AMT	Amount of something
DOC_ID 	Document identifier
PETITIONER	Name of the petitioners / appellants /revisionist from current case
RESPONDENT	Name of the respondents / defendents /opposition from current case
COURT	Name of the court which has delivered the current judgement
STATUTE	Name of the act or law mentioned in the judgement
PROVISION	Sections, sub-sections, articles, orders, rules under a statute"""

f = open("sample_data_160424/LAW000026.txt", "r", encoding="utf-8")
#f = open("sample_data_160424/CASE000001.txt", "r", encoding="utf-8")
data = f.read()
print(model.get_label_list(labels_case_dan_su, data)) 