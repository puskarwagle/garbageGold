

# from personals import *
# import json

###################################################### CONFIGURE YOUR RESUME HERE ######################################################

from personals import *
import json
from pathlib import Path

###################################################### CONFIGURE YOUR RESUME HERE ######################################################

# You don't need to edit this file if you've already added your default resume.
default_resume_path = Path("all resumes/default/resume.pdf")

if not default_resume_path.exists():
    print("[⚠️] Resume not found at:", default_resume_path)
    print("[ℹ️] Will fallback to previously uploaded resume on LinkedIn.")
else:
    print("[✅] Resume loaded:", default_resume_path)

# Prepare resume metadata in JSON-like format
resume_headline = {
    "full_name": f"{first_name} {last_name}",
    "email": email,
    "phone": phone,
    "location": location,
    "headline": linkedin_headline,
    "summary": linkedin_summary.strip(),
    "linkedin": linkedIn,
    "portfolio": website,
    "current_title": title,
    "years_of_experience": years_of_experience,
    "confidence_score": confidence_level,
    "current_employer": recent_employer,
    "notice_period_days": notice_period,
    "citizenship_status": us_citizenship,
    "expected_ctc": desired_salary,
    "current_ctc": current_ctc,
    "cover_letter": cover_letter.strip(),
    "user_bio": user_information_all.strip(),
}

# Optional: export to a .json file (e.g., for AI prompt use)
def export_resume_json(path="resume_metadata.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(resume_headline, f, indent=4)
    print(f"[📤] Resume metadata exported to {path}")

# Call export if needed
if __name__ == "__main__":
    export_resume_json()

# # Give an relative path of your default resume to be uploaded. If file in not found, will continue using your previously uploaded resume in LinkedIn.
# default_resume_path = "all resumes/default/resume.pdf"      # (In Development)

'''
YOU DON'T HAVE TO EDIT THIS FILE, IF YOU ADDED YOUR DEFAULT RESUME.
'''


# resume_headline = json({
#     "first_name": first_name,
# })











# # >>>>>>>>>>> RELATED SETTINGS <<<<<<<<<<<

# ## Allow Manual Inputs
# # Should the tool pause before every submit application during easy apply to let you check the information?
# pause_before_submit = True         # True or False, Note: True or False are case-sensitive
# '''
# Note: Will be treated as False if `run_in_background = True`
# '''

# # Should the tool pause if it needs help in answering questions during easy apply?
# # Note: If set as False will answer randomly...
# pause_at_failed_question = True    # True or False, Note: True or False are case-sensitive
# '''
# Note: Will be treated as False if `run_in_background = True`
# '''
# ##

# # Do you want to overwrite previous answers?
# overwrite_previous_answers = False # True or False, Note: True or False are case-sensitive





