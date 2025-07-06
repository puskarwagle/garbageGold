import os
import csv
import re
import pyautogui
from dataclasses import dataclass, field
from typing import Set, List, Optional, Tuple, Dict, Any
from datetime import datetime
from random import choice, shuffle, randint
from enum import Enum
from utils.logger import log, log_error

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    NoSuchElementException, 
    ElementClickInterceptedException, 
    NoSuchWindowException, 
    ElementNotInteractableException
)

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Import configurations and utilities
from config.personals import *
from config.questions import *
from config.search import *
from config.secrets import use_AI, username, password, ai_provider
from config.settings import *
from browser.open_chrome import launch_browser
from utils.helpers import *
from browser.clickers_and_finders import *
from utils.validator import validate_config
from ai.openaiConnections import ai_create_openai_client, ai_extract_skills, ai_answer_question, ai_close_openai_client
from ai.deepseekConnections import deepseek_create_client, deepseek_extract_skills, deepseek_answer_question


class ApplicationResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    EXTERNAL = "external"


@dataclass
class UserProfile:
    """User's personal and professional information"""
    first_name: str
    middle_name: str
    last_name: str
    current_city: str
    desired_salary: int
    current_ctc: int
    notice_period: int
    
    def __post_init__(self):
        self.first_name = self.first_name.strip()
        self.middle_name = self.middle_name.strip()
        self.last_name = self.last_name.strip()
        self.current_city = self.current_city.strip()
    
    @property
    def full_name(self) -> str:
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def salary_lakhs(self) -> str:
        return str(round(self.desired_salary / 100000, 2))
    
    @property
    def salary_monthly(self) -> str:
        return str(round(self.desired_salary / 12, 2))
    
    @property
    def ctc_lakhs(self) -> str:
        return str(round(self.current_ctc / 100000, 2))
    
    @property
    def ctc_monthly(self) -> str:
        return str(round(self.current_ctc / 12, 2))
    
    @property
    def notice_period_months(self) -> str:
        return str(self.notice_period // 30)
    
    @property
    def notice_period_weeks(self) -> str:
        return str(self.notice_period // 7)


@dataclass
class JobStats:
    """Tracking application statistics"""
    easy_applied_count: int = 0
    external_jobs_count: int = 0
    failed_count: int = 0
    skip_count: int = 0
    tabs_count: int = 1
    
    @property
    def total_applied(self) -> int:
        return self.easy_applied_count + self.external_jobs_count
    
    def increment_easy_applied(self):
        self.easy_applied_count += 1
    
    def increment_external(self):
        self.external_jobs_count += 1
    
    def increment_failed(self):
        self.failed_count += 1
    
    def increment_skipped(self):
        self.skip_count += 1


@dataclass
class AIConfig:
    """AI-related configuration"""
    enabled: bool
    provider: str
    client: Any = None
    
    def initialize_client(self):
        if not self.enabled:
            return
        
        log(f"Initializing AI client for {self.provider}...")
        if self.provider.lower() == "openai":
            self.client = ai_create_openai_client()
        elif self.provider.lower() == "deepseek":
            self.client = deepseek_create_client()
        else:
            log(f"Unknown AI provider: {self.provider}")
            self.client = None
    
    def extract_skills(self, description: str) -> str:
        if not self.client:
            return "AI not available"
        
        try:
            if self.provider.lower() == "openai":
                return ai_extract_skills(self.client, description)
            elif self.provider.lower() == "deepseek":
                return deepseek_extract_skills(self.client, description)
            return "Unsupported AI provider"
        except Exception as e:
            log("Failed to extract skills:", e)
            return "Error extracting skills"
    
    def close_client(self):
        if self.client:
            try:
                ai_close_openai_client(self.client)
                log(f"Closed {self.provider} AI client.")
            except Exception as e:
                log("Failed to close AI client:", e)


@dataclass
class JobDetails:
    """Job information container"""
    job_id: str
    title: str
    company: str
    work_location: str
    work_style: str
    description: str = "Unknown"
    experience_required: str = "Unknown"
    skills: str = "Unknown"
    date_listed: str = "Unknown"
    hr_name: str = "Unknown"
    hr_link: str = "Unknown"
    job_link: str = ""
    reposted: bool = False
    
    def __post_init__(self):
        if not self.job_link:
            self.job_link = f"https://www.linkedin.com/jobs/view/{self.job_id}"


@dataclass
class ApplicationConfig:
    """Application behavior configuration"""
    pause_before_submit: bool
    pause_at_failed_question: bool
    run_non_stop: bool
    use_new_resume: bool
    keep_screen_awake: bool
    randomize_search_order: bool
    daily_limit_reached: bool = False
    
    def __post_init__(self):
        if run_in_background:
            self.pause_at_failed_question = False
            self.pause_before_submit = False
            self.run_non_stop = False


class JobApplier:
    """Main job application orchestrator"""
    
    def __init__(self):
        self.user_profile = UserProfile(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            current_city=current_city,
            desired_salary=desired_salary,
            current_ctc=current_ctc,
            notice_period=notice_period
        )
        
        self.stats = JobStats()
        self.ai_config = AIConfig(enabled=use_AI, provider=ai_provider)
        self.app_config = ApplicationConfig(
            pause_before_submit=pause_before_submit,
            pause_at_failed_question=pause_at_failed_question,
            run_non_stop=run_non_stop,
            use_new_resume=True,
            keep_screen_awake=keep_screen_awake,
            randomize_search_order=randomize_search_order
        )
        
        # Browser and state
        self.driver = None
        self.wait = None
        self.actions = None
        self.linkedin_tab = None
        self.applied_jobs: Set[str] = set()
        self.rejected_jobs: Set[str] = set()
        self.blacklisted_companies: Set[str] = set()
        self.randomly_answered_questions: Set[str] = set()
        
        # Constants
        self.EXPERIENCE_REGEX = re.compile(r'[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?', re.IGNORECASE)
        
        pyautogui.FAILSAFE = False
    
    def initialize_browser(self):
        """Initialize browser and authentication"""
        self.driver, self.wait, self.actions = launch_browser()
        self.stats.tabs_count = len(self.driver.window_handles)
        
        # Login to LinkedIn
        self.driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN():
            login_LN()
        self.linkedin_tab = self.driver.current_window_handle
    
    def initialize_ai(self):
        """Initialize AI client if enabled"""
        self.ai_config.initialize_client()
    
    def validate_resume(self) -> bool:
        """Check if resume exists and is accessible"""
        if not os.path.exists(default_resume_path):
            pyautogui.alert(
                text=f'Your default resume "{default_resume_path}" is missing! '
                     'Please update the path in config.py or add the resume file.',
                title="Missing Resume",
                button="OK"
            )
            self.app_config.use_new_resume = False
            return False
        return True
    
    def get_job_basic_info(self, job_element) -> Tuple[Optional[JobDetails], bool]:
        """Extract basic job information from listing element"""
        try:
            job_id, title, company, work_location, work_style, skip = get_job_main_details(
                job_element, self.blacklisted_companies, self.rejected_jobs
            )
            
            if skip:
                return None, True
            
            # Check if already applied
            if job_id in self.applied_jobs or find_by_class(self.driver, "jobs-s-apply__application-link", 2):
                log(f'Already applied to "{title} | {company}" job. Job ID: {job_id}!')
                return None, True
            
            job_details = JobDetails(
                job_id=job_id,
                title=title,
                company=company,
                work_location=work_location,
                work_style=work_style
            )
            
            return job_details, False
            
        except Exception as e:
            log("Failed to extract job basic info:", e)
            return None, True
    
    def enrich_job_details(self, job_details: JobDetails) -> Tuple[JobDetails, bool]:
        """Enrich job details with additional information"""
        try:
            # Check blacklist
            self.rejected_jobs, self.blacklisted_companies, jobs_top_card = check_blacklist(
                self.rejected_jobs, job_details.job_id, job_details.company, self.blacklisted_companies
            )
            
            # Get HR information
            self._extract_hr_info(job_details)
            
            # Get posting date
            self._extract_posting_date(job_details, jobs_top_card)
            
            # Get job description
            description, experience_required, skip, reason, message = get_job_description()
            if skip:
                log(message)
                failed_job(job_details.job_id, job_details.job_link, "Pending", 
                          job_details.date_listed, reason, message, "Skipped", "Not Available")
                self.rejected_jobs.add(job_details.job_id)
                self.stats.increment_skipped()
                return job_details, True
            
            job_details.description = description
            job_details.experience_required = experience_required
            
            # Extract skills using AI
            if self.ai_config.enabled and description != "Unknown":
                job_details.skills = self.ai_config.extract_skills(description)
                log(f"Extracted skills using {self.ai_config.provider} AI")
            
            return job_details, False
            
        except ValueError as e:
            log(e, 'Skipping this job!')
            failed_job(job_details.job_id, job_details.job_link, "Pending", 
                      job_details.date_listed, "Found Blacklisted words", str(e), "Skipped", "Not Available")
            self.stats.increment_skipped()
            return job_details, True
        except Exception as e:
            log("Failed to enrich job details:", e)
            return job_details, True
    
    def _extract_hr_info(self, job_details: JobDetails):
        """Extract hiring manager information"""
        try:
            hr_info_card = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hirer-card__hirer-information"))
            )
            job_details.hr_link = hr_info_card.find_element(By.TAG_NAME, "a").get_attribute("href")
            job_details.hr_name = hr_info_card.find_element(By.TAG_NAME, "span").text
        except Exception as e:
            log(f'HR info not available for "{job_details.title}" (ID: {job_details.job_id})')
    
    def _extract_posting_date(self, job_details: JobDetails, jobs_top_card):
        """Extract and calculate job posting date"""
        try:
            time_posted_text = jobs_top_card.find_element(
                By.XPATH, './/span[contains(normalize-space(), " ago")]'
            ).text
            print(f"Time Posted: {time_posted_text}")
            
            if "Reposted" in time_posted_text:
                job_details.reposted = True
                time_posted_text = time_posted_text.replace("Reposted", "")
            
            job_details.date_listed = calculate_date_posted(time_posted_text)
        except Exception as e:
            log("Failed to calculate posting date:", e)
    
    def apply_to_job(self, job_details: JobDetails) -> ApplicationResult:
        """Apply to a single job"""
        try:
            # Try Easy Apply first
            if try_xp(self.driver, ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3') and contains(@aria-label, 'Easy')]"):
                return self._easy_apply(job_details)
            else:
                return self._external_apply(job_details)
        except Exception as e:
            log("Failed to apply to job:", e)
            self.stats.increment_failed()
            return ApplicationResult.FAILED
    
    def _easy_apply(self, job_details: JobDetails) -> ApplicationResult:
        """Handle Easy Apply process"""
        try:
            modal = find_by_class(self.driver, "jobs-easy-apply-modal")
            wait_span_click(modal, "Next", 1)
            
            resume = "Previous resume"
            uploaded = False
            questions_list = set()
            next_counter = 0
            
            # Process application steps
            while True:
                next_counter += 1
                if next_counter >= 15:
                    if self.app_config.pause_at_failed_question:
                        self._handle_manual_intervention(job_details.job_id)
                        next_counter = 1
                        continue
                    else:
                        raise Exception("Stuck in continuous loop - probably new questions")
                
                questions_list = answer_questions(
                    modal, questions_list, job_details.work_location, 
                    job_description=job_details.description
                )
                
                if self.app_config.use_new_resume and not uploaded:
                    uploaded, resume = upload_resume(modal, default_resume_path)
                
                try:
                    next_button = modal.find_element(By.XPATH, './/span[normalize-space(.)="Review"]')
                except NoSuchElementException:
                    next_button = modal.find_element(By.XPATH, './/button[contains(span, "Next")]')
                
                try:
                    next_button.click()
                except ElementClickInterceptedException:
                    break
                
                buffer(click_gap)
            
            # Final submission
            if self._handle_submission(job_details, questions_list):
                if uploaded:
                    self.app_config.use_new_resume = False
                self.stats.increment_easy_applied()
                return ApplicationResult.SUCCESS
            else:
                self.stats.increment_failed()
                return ApplicationResult.FAILED
                
        except Exception as e:
            log("Easy Apply failed:", e)
            self.stats.increment_failed()
            discard_job()
            return ApplicationResult.FAILED
    
    def _external_apply(self, job_details: JobDetails) -> ApplicationResult:
        """Handle external application process"""
        try:
            skip, application_link, self.stats.tabs_count = external_apply(
                None, job_details.job_id, job_details.job_link, "Pending",
                job_details.date_listed, "External", "Not Available"
            )
            
            if self.app_config.daily_limit_reached:
                log("Daily application limit reached!")
                return ApplicationResult.FAILED
            
            if skip:
                return ApplicationResult.SKIPPED
            
            self.stats.increment_external()
            return ApplicationResult.EXTERNAL
            
        except Exception as e:
            log("External apply failed:", e)
            self.stats.increment_failed()
            return ApplicationResult.FAILED
    
    def _handle_submission(self, job_details: JobDetails, questions_list: set) -> bool:
        """Handle final application submission"""
        try:
            wait_span_click(self.driver, "Review", 1, scrollTop=True)
            
            if self.app_config.pause_before_submit:
                decision = pyautogui.confirm(
                    '1. Please verify your information.\n'
                    '2. If you edited something, please return to this final screen.\n'
                    '3. DO NOT CLICK "Submit Application".\n\n'
                    'You can turn off "Pause before submit" in config.py',
                    "Confirm your information",
                    ["Disable Pause", "Discard Application", "Submit Application"]
                )
                
                if decision == "Discard Application":
                    raise Exception("Job application discarded by user!")
                
                if decision == "Disable Pause":
                    self.app_config.pause_before_submit = False
            
            follow_company(find_by_class(self.driver, "jobs-easy-apply-modal"))
            
            if wait_span_click(self.driver, "Submit application", 2, scrollTop=True):
                date_applied = datetime.now()
                if not wait_span_click(self.driver, "Done", 2):
                    self.actions.send_keys(Keys.ESCAPE).perform()
                return True
            
            return False
            
        except Exception as e:
            log("Submission failed:", e)
            return False
    
    def _handle_manual_intervention(self, job_id: str):
        """Handle manual intervention for difficult questions"""
        screenshot(self.driver, job_id, "Needed manual intervention")
        pyautogui.alert(
            "Couldn't answer one or more questions.\n"
            "Please click \"Continue\" once done.\n"
            "DO NOT CLICK Back, Next or Review button in LinkedIn.",
            "Help Needed",
            "Continue"
        )
    
    def process_search_term(self, search_term: str) -> int:
        """Process jobs for a specific search term"""
        self.driver.get(f"https://www.linkedin.com/jobs/search/?keywords={search_term}")
        log(f'\n>>>> Now searching for "{search_term}" <<<<\n')
        
        apply_filters()
        
        current_count = 0
        
        try:
            while current_count < switch_number:
                # Wait for job listings
                self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-occludable-job-id]")))
                
                pagination_element, current_page = get_page_info()
                buffer(3)
                
                job_listings = self.driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")
                
                for job_element in job_listings:
                    if self.app_config.keep_screen_awake:
                        pyautogui.press('shiftright')
                    
                    if current_count >= switch_number:
                        break
                    
                    log("\n-@-\n")
                    
                    # Get basic job info
                    job_details, skip = self.get_job_basic_info(job_element)
                    if skip:
                        continue
                    
                    # Enrich with additional details
                    job_details, skip = self.enrich_job_details(job_details)
                    if skip:
                        continue
                    
                    # Apply to job
                    result = self.apply_to_job(job_details)
                    
                    if result == ApplicationResult.SUCCESS:
                        self._save_successful_application(job_details)
                        self.applied_jobs.add(job_details.job_id)
                        current_count += 1
                        log(f'Successfully applied to "{job_details.title} | {job_details.company}"')
                    elif result == ApplicationResult.EXTERNAL:
                        current_count += 1
                
                # Move to next page
                if not self._navigate_to_next_page(pagination_element, current_page):
                    break
                    
        except Exception as e:
            log("Failed to process search term:", e)
            log_error("In process_search_term", e)
        
        return current_count
    
    def _save_successful_application(self, job_details: JobDetails):
        """Save successful application to database/file"""
        submitted_jobs(
            job_details.job_id,
            job_details.title,
            job_details.company,
            job_details.work_location,
            job_details.work_style,
            job_details.description,
            job_details.experience_required,
            job_details.skills,
            job_details.hr_name,
            job_details.hr_link,
            "Previous resume",  # TODO: track actual resume used
            job_details.reposted,
            job_details.date_listed,
            datetime.now(),
            job_details.job_link,
            "Easy Applied",
            set(),  # TODO: track questions
            "In Development"
        )
    
    def _navigate_to_next_page(self, pagination_element, current_page: int) -> bool:
        """Navigate to next page of results"""
        if pagination_element is None:
            log("No pagination element found - probably at end of results")
            return False
        
        try:
            next_page_button = pagination_element.find_element(
                By.XPATH, f"//button[@aria-label='Page {current_page + 1}']"
            )
            next_page_button.click()
            log(f"\n>-> Now on Page {current_page + 1}\n")
            return True
        except NoSuchElementException:
            log(f"Page {current_page + 1} not found - probably at end of results")
            return False
    
    def run_application_cycle(self, search_terms: List[str]) -> int:
        """Run one complete application cycle"""
        if self.app_config.randomize_search_order:
            shuffle(search_terms)
        
        total_processed = 0
        
        for search_term in search_terms:
            if self.app_config.daily_limit_reached:
                break
            
            processed = self.process_search_term(search_term)
            total_processed += processed
            
            log(f"Processed {processed} jobs for search term: {search_term}")
        
        return total_processed
    
    def run_continuous(self, search_terms: List[str]):
        """Run continuous application cycles"""
        total_runs = 1
        self.applied_jobs = get_applied_job_ids()
        
        log(f"Starting continuous run with {len(search_terms)} search terms")
        
        try:
            while True:
                log(f"\n{'='*100}")
                log(f"Cycle {total_runs} - {datetime.now()}")
                log(f"Looking for jobs posted within '{date_posted}' sorted by '{sort_by}'")
                
                processed = self.run_application_cycle(search_terms)
                
                log(f"Cycle {total_runs} completed - processed {processed} jobs")
                log(f"{'='*100}\n")
                
                if self.app_config.daily_limit_reached:
                    log("Daily limit reached - stopping")
                    break
                
                if not self.app_config.run_non_stop:
                    break
                
                # Handle cycling options
                if cycle_date_posted:
                    self._cycle_date_posted()
                if alternate_sortby:
                    self._alternate_sort_by()
                
                total_runs += 1
                
                # Sleep between cycles
                log("Sleeping for 10 minutes...")
                sleep(600)
                
        except KeyboardInterrupt:
            log("Application stopped by user")
        except Exception as e:
            log("Error in continuous run:", e)
            log_error("In run_continuous", e)
        
        return total_runs
    
    def _cycle_date_posted(self):
        """Cycle through date posted options"""
        global date_posted
        date_options = ["Any time", "Past month", "Past week", "Past 24 hours"]
        current_index = date_options.index(date_posted)
        
        if stop_date_cycle_at_24hr and current_index == len(date_options) - 1:
            date_posted = date_options[0]
        else:
            date_posted = date_options[(current_index + 1) % len(date_options)]
    
    def _alternate_sort_by(self):
        """Alternate between sort by options"""
        global sort_by
        sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
    
    def print_final_stats(self, total_runs: int):
        """Print final application statistics"""
        log("\n" + "="*60)
        log("FINAL STATISTICS")
        log("="*60)
        log(f"Total runs:                     {total_runs}")
        log(f"Jobs Easy Applied:              {self.stats.easy_applied_count}")
        log(f"External job links collected:   {self.stats.external_jobs_count}")
        log(f"                              ----------")
        log(f"Total applied or collected:     {self.stats.total_applied}")
        log(f"\nFailed jobs:                    {self.stats.failed_count}")
        log(f"Irrelevant jobs skipped:        {self.stats.skip_count}")
        
        if self.randomly_answered_questions:
            log(f"\nQuestions randomly answered:\n{'; '.join(self.randomly_answered_questions)}")
        
        # Inspirational quote
        quotes = [
            "You're one step closer than before.",
            "All the best with your future interviews.",
            "Keep up with the progress. You got this.",
            "If you're tired, learn to take rest but never give up.",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence.",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs",
            "Opportunities don't happen, you create them. - Chris Grosser",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance.",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt"
        ]
        
        quote = choice(quotes)
        final_msg = f"\n{quote}\n\nBest regards,\nSai Vignesh Golla\nhttps://www.linkedin.com/in/saivigneshgolla/"
        
        log(final_msg)
        pyautogui.alert(final_msg, "Application Complete")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.ai_config.close_client()
            
            if self.stats.tabs_count >= 10:
                warning_msg = ("NOTE: You have 10+ tabs open. Please close or bookmark them!\n"
                             "Otherwise, the application might not work properly next time.")
                pyautogui.alert(warning_msg, "Warning")
                log(warning_msg)
            
            if self.driver:
                self.driver.quit()
                log("Browser closed successfully")
                
        except Exception as e:
            log("Error during cleanup:", e)
            log_error("During cleanup", e)


def linkedinMain():
    """Main application entry point"""
    applier = JobApplier()
    
    try:
        # Initialize components
        validate_config()
        applier.initialize_browser()
        applier.initialize_ai()
        applier.validate_resume()
        
        # Run application process
        total_runs = applier.run_continuous(search_terms)
        
    except NoSuchWindowException:
        log("Browser window closed")
    except Exception as e:
        log("Critical error in main:", e)
        log_error("In main", e)
        pyautogui.alert(str(e), "Critical Error")
    finally:
        applier.print_final_stats(total_runs if 'total_runs' in locals() else 1)
        applier.cleanup()


if __name__ == "__main__":
    linkedinMain()