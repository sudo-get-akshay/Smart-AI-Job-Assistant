import os
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import pdfplumber
import requests

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAOKjR50CAQqb8jDLPk9D61UY8n8JPdJAk")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "861de00f6cd47136e119e04a65dd6107dd18bc14fe0343d19f48892339d0c00b")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyD6z0gu_tAdqk2M5186TS9wgbsfbgyYMaI")

GEMINI_MODEL = "gemini-1.5-flash"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
SERPAPI_URL = "https://serpapi.com/search"

# ============================================
# PDF PROCESSING
# ============================================
def load_pdf_text(uploaded_file: Any) -> str:
    """Extracts text from an uploaded PDF file."""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages).strip()
    except Exception as e:
        print(f"Error processing PDF file: {e}")
        return ""

# ============================================
# RESUME ANALYSIS
# ============================================
def extract_resume_skills(resume_text: str) -> List[str]:
    """Identifies technical skills in the resume text."""
    skill_categories = {
    "Programming Languages": ["python", "java", "c++", "javascript", "typescript", "sql", "nosql", "go", "rust", "c#", "php", "ruby", "swift", "kotlin", "perl", "scala", "haskell", "r", "matlab", "dart", "lua"],
    "AI/ML": ["ai", "ml", "nlp", "deep learning", "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn", "machine learning", "neural networks", "llm", "natural language processing", "robotics", "reinforcement learning", "gpt", "bert", "transformers", "langchain", "hugging face", "openai", "gemini"],
    "Cloud & DevOps": ["cloud", "aws", "gcp", "azure", "docker", "kubernetes", "git", "ci/cd", "jenkins", "terraform", "ansible", "devops", "serverless", "microservices", "gitlab", "github actions", "circleci", "cloudformation", "helm", "prometheus", "grafana"],
    "Frameworks & Libraries": ["react", "angular", "vue", "node", "express", "django", "flask", "spring", "fastapi", "next.js", "svelte", "ember", "backbone", "jquery", "bootstrap", "tailwind", "material-ui", "redux", "webpack", "vite", "nest.js", "laravel", "rails", "asp.net"],
    "Mobile Development": ["android", "ios", "react native", "flutter", "xamarin", "ionic", "swift", "kotlin", "objective-c", "mobile app development", "app store", "play store"],
    "Game Development": ["unity", "unreal engine", "godot", "game development", "3d modeling", "blender", "maya", "game design", "c++", "c#", "opengl", "directx", "vulkan", "shader programming", "physics engine", "ar", "vr", "augmented reality", "virtual reality"],
    "Data & Analytics": ["data science", "data analysis", "statistics", "spark", "hadoop", "kafka", "elasticsearch", "etl", "data engineering", "big data", "data visualization", "business intelligence", "tableau", "power bi", "looker", "pandas", "numpy", "matplotlib", "seaborn", "jupyter", "airflow", "dbt"],
    "Web Development": ["html", "css", "rest api", "graphql", "microservices", "web development", "frontend", "backend", "full stack", "web security", "web performance", "sass", "less", "webpack", "responsive design", "seo", "pwa", "webassembly"],
    "Databases": ["mongodb", "postgresql", "mysql", "redis", "cassandra", "dynamodb", "oracle", "sql server", "firebase", "supabase", "prisma", "sequelize", "typeorm", "sqlite", "mariadb", "neo4j", "couchdb", "elasticsearch"],
    "Methodologies & Practices": ["agile", "scrum", "kanban", "devops", "tdd", "bdd", "ci/cd", "continuous integration", "continuous deployment", "pair programming", "code review", "design patterns", "clean code", "solid principles", "microservices architecture"],
    "Cybersecurity": ["security", "cybersecurity", "network security", "application security", "data security", "compliance", "risk management", "penetration testing", "ethical hacking", "vulnerability assessment", "encryption", "authentication", "authorization", "owasp", "soc", "siem"],
    "Networking": ["networking", "tcp/ip", "dns", "http", "https", "network architecture", "network administration", "vpn", "firewall", "load balancing", "cdn", "websockets"], 
    "Operating Systems": ["linux", "windows", "macos", "unix", "ubuntu", "centos", "debian", "redhat", "bash", "powershell", "shell scripting"],    
    "Blockchain & Web3": ["blockchain", "web3", "ethereum", "solidity", "smart contracts", "cryptocurrency", "nft", "defi", "bitcoin", "polygon", "hyperledger"],  
    "Design & UI/UX": ["ui/ux", "figma", "sketch", "adobe xd", "photoshop", "illustrator", "user experience", "user interface", "wireframing", "prototyping", "design thinking", "accessibility"],
    "Testing & QA": ["testing", "unit testing", "integration testing", "e2e testing", "selenium", "cypress", "jest", "mocha", "pytest", "junit", "automation testing", "manual testing", "qa", "quality assurance"],
    "Version Control": ["git", "github", "gitlab", "bitbucket", "svn", "version control", "source control"],
    "Project Management": ["jira", "trello", "asana", "monday.com", "project management", "product management", "stakeholder management"],
}
    
    all_skills = [skill for category in skill_categories.values() for skill in category]
    resume_lower = resume_text.lower()
    found_skills = {skill.title() if not skill.isupper() else skill for skill in all_skills if skill in resume_lower}
    
    return list(found_skills) if found_skills else ["Software Engineer"]

def extract_resume_details(resume_text: str) -> Dict[str, Optional[str]]:
    """Extracts contact information from the resume."""
    details = {"name": "Candidate", "phone": "[Phone Number]", "email": "[Email Address]"}
    
    try:
        # Extract phone number
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", resume_text)
        if phone_match:
            details["phone"] = phone_match.group(0)

        # Extract email
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resume_text)
        if email_match:
            details["email"] = email_match.group(0)

        # Extract name (first line with 2-4 words, no digits)
        for line in resume_text.split('\n'):
            clean_line = line.strip()
            if 2 <= len(clean_line.split()) <= 4 and not any(char.isdigit() for char in clean_line):
                details["name"] = clean_line
                break
    
    except Exception as e:
        print(f"Warning: Error extracting resume details: {e}")
            
    return details

# ============================================
# HELPER FUNCTIONS FOR JOB SEARCH
# ============================================
def _extract_company_name(title: str, displayed_link: str, url: str) -> str:
    """Helper function to extract a company name from search results."""
    # Try extracting from title (format: "Job Title - Company Name")
    if " - " in title:
        company = title.split(" - ")[-1].strip()
        if not any(x in company.lower() for x in ["jobs", "careers", "apply", "hiring"]):
            return company
    
    # Try extracting from displayed link
    if displayed_link:
        company = displayed_link.split(" › ")[0].strip()
        if company and not any(x in company.lower() for x in ["www", "http", "jobs"]):
            return company
    
    # Extract from URL domain
    try:
        domain = urlparse(url).netloc.replace("www.", "").replace("jobs.", "").replace("careers.", "")
        company = domain.split(".")[0].title()
        return company if company else "Unknown Company"
    except:
        return "Unknown Company"

def _clean_job_title(title: str) -> str:
    """Helper function to remove company names and other noise from job titles."""
    return re.split(r' - | \| | at ', title)[0].strip()

# ============================================
# JOB SEARCH
# ============================================
def search_jobs(skills, location: str = "India", limit: int = 8) -> List[Dict[str, Any]]:
    """Fetches job listings from SerpAPI Google Jobs."""
    
    # ✅ FIX: Handle both dict and list inputs
    all_skills = []
    
    if isinstance(skills, dict):
        # If skills is a dictionary (from extract_resume_skills)
        for category, skill_list in skills.items():
            all_skills.extend(skill_list[:3])  # Take top 3 from each category
    elif isinstance(skills, list):
        # If skills is already a list (from Flask API)
        all_skills = skills[:10]  # Take top 10 skills
    else:
        print(f"⚠️ Unexpected skills type: {type(skills)}")
        all_skills = ["software engineer"]
    
    # Use top skills for query
    top_skills = all_skills[:5] if all_skills else ["software engineer"]
    query = f"{' '.join(top_skills)} jobs in {location}"
    
    print(f"🔎 Job search query: {query}")
    
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SERPAPI_KEY,
        "location": location,
        "hl": "en",
        "gl": "in"
    }
    
    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        print(f"✅ API Response: {len(data.get('jobs_results', []))} jobs found")

        jobs = []
        for item in data.get("jobs_results", [])[:limit]:
            apply_options = item.get("apply_options", [])
            link = apply_options[0].get("link") if apply_options else item.get("share_url", "#")
            description = item.get("description", "")
            
            jobs.append({
                "title": item.get("title", "Untitled"),
                "company": item.get("company_name", "Unknown Company"),
                "location": item.get("location", location),
                "description": description[:300] + "..." if len(description) > 300 else description,
                "link": link,
            })
        
        if jobs:
            print(f"✅ Returning {len(jobs)} jobs from primary search")
            return jobs
        
    except requests.RequestException as e:
        print(f"❌ SerpAPI job search failed: {e}")

    return search_jobs_alternative(all_skills, location, limit)


def search_jobs_alternative(skills, location: str, limit: int) -> List[Dict[str, Any]]:
    """Alternative job search using general Google search via SerpAPI."""
    
    # ✅ Ensure skills is a list
    if isinstance(skills, dict):
        all_skills = []
        for skill_list in skills.values():
            all_skills.extend(skill_list[:3])
        skills = all_skills
    elif isinstance(skills, list):
        skills = skills[:10]  # Already a list, just limit it
    else:
        skills = ["software engineer"]
    
    top_skills = skills[:3] if skills else ["software engineer"]
    query = f"{' '.join(top_skills)} job openings {location} apply 2025"
    
    print(f"🔎 Alternative search query: {query}")
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": limit * 2,
        "gl": "in",
        "hl": "en"
    }

    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Alternative API Response: {len(data.get('organic_results', []))} results")

        jobs = []
        job_indicators = {"hiring", "apply", "career", "jobs/view", "job-details", "opening", "vacancy"}
        portal_keywords = {"search?", "jobs?", "browse", "find-jobs", "job-search"}
        
        for item in data.get("organic_results", []):
            link = item.get("link", "")
            title = item.get("title", "")
            
            # Skip portal search pages
            if any(keyword in link.lower() for keyword in portal_keywords):
                continue
            
            # Only include actual job postings
            if any(indicator in link.lower() or indicator in title.lower() for indicator in job_indicators):
                company = _extract_company_name(title, item.get("displayed_link", ""), link)
                snippet = item.get("snippet", "")
                
                jobs.append({
                    "title": _clean_job_title(title),
                    "company": company,
                    "location": location,
                    "description": snippet[:300] + "..." if len(snippet) > 300 else snippet,
                    "link": link,
                })
                
                if len(jobs) >= limit:
                    break
        
        if jobs:
            print(f"✅ Returning {len(jobs)} jobs from alternative search")
            return jobs
        else:
            print("⚠️ No jobs found in alternative search, using fallback")

    except requests.RequestException as e:
        print(f"❌ Alternative job search failed: {e}")

    # Fallback jobs with legitimate links
    print("⚠️ Using fallback jobs")
    return [
        {
            "title": "Software Engineer",
            "company": "Flipkart",
            "location": "Bangalore, India",
            "description": "Join India's leading e-commerce company. Work on scalable systems serving millions of users daily.",
            "link": "https://www.flipkartcareers.com/"
        },
        {
            "title": "Full Stack Developer",
            "company": "Razorpay",
            "location": "Bangalore, India",
            "description": "Build innovative payment solutions. Work with modern tech stack and fintech products.",
            "link": "https://razorpay.com/jobs/"
        },
        {
            "title": "Backend Engineer",
            "company": "Swiggy",
            "location": "Bangalore, India",
            "description": "Build real-time systems for food delivery. Work with microservices and high-scale architecture.",
            "link": "https://careers.swiggy.com/"
        },
        {
            "title": "Data Scientist",
            "company": "PhonePe",
            "location": "Bangalore, India",
            "description": "Work on ML models for fraud detection and recommendations. Analyze payment data at scale.",
            "link": "https://www.phonepe.com/careers/"
        },
        {
            "title": "ML Engineer",
            "company": "Ola",
            "location": "Bangalore, India",
            "description": "Build ML systems for ride allocation and demand prediction. Work with real-time data.",
            "link": "https://www.olacabs.com/careers"
        },
        {
            "title": "Frontend Developer",
            "company": "CRED",
            "location": "Bangalore, India",
            "description": "Create premium user experiences. Work with React, animations, and modern design systems.",
            "link": "https://careers.cred.club/"
        },
        {
            "title": "DevOps Engineer",
            "company": "Zomato",
            "location": "Gurugram, India",
            "description": "Manage cloud infrastructure and deployment pipelines. Work with AWS and Kubernetes.",
            "link": "https://www.zomato.com/careers"
        },
        {
            "title": "Software Developer",
            "company": "Freshworks",
            "location": "Chennai, India",
            "description": "Build SaaS products used by businesses worldwide. Work on customer engagement platforms.",
            "link": "https://www.freshworks.com/company/careers/"
        }
    ]
# ============================================
# AI CONTENT GENERATION
# ============================================
def generate_cover_letter(resume_text: str, job: Dict[str, Any]) -> str:
    """Generates a cover letter using direct Gemini API."""
    try:
        import google.generativeai as genai
        
        details = extract_resume_details(resume_text)
        
        # Safely extract and clean job details
        job_title = str(job.get('title', 'Position')).strip()
        company = str(job.get('company', 'Company')).strip()
        description = str(job.get('description', ''))[:500].strip()

        print(f"\n{'='*60}")
        print(f"Generating cover letter for: {company} - {job_title}")
        print(f"{'='*60}\n")

        # Configure Gemini API directly
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Write a professional cover letter for this job application:

Position: {job_title}
Company: {company}
Job Description: {description}

Applicant Details:
- Name: {details['name']}
- Email: {details['email']}
- Phone: {details['phone']}

Key Skills from Resume:
{resume_text[:800]}

Write a concise 3-paragraph cover letter that:
1. Opens with enthusiasm for the specific role
2. Highlights 2-3 relevant skills or experiences
3. Closes with a strong call to action

Keep it professional, personable, and under 300 words."""
        
        response = model.generate_content(prompt)
        letter = response.text
        
        print(f"✓ Cover letter generated successfully ({len(letter)} characters)\n")
        return letter
        
    except Exception as e:
        print(f"✗ Error generating cover letter: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return fallback template
        details = extract_resume_details(resume_text)
        return f"""Dear Hiring Manager,

I am excited to apply for the {job.get('title', 'position')} position at {job.get('company', 'your company')}. With my relevant background and skills, I am confident I would be a valuable addition to your team.

My experience aligns well with the requirements outlined in your job description. I am particularly drawn to this opportunity because it combines my technical expertise with my passion for innovation and problem-solving. I have consistently demonstrated the ability to deliver high-quality results and collaborate effectively with cross-functional teams.

I would welcome the opportunity to discuss how I can contribute to {job.get('company', 'your organization')}'s success. Thank you for considering my application, and I look forward to speaking with you soon.

Best regards,
{details.get('name', 'Candidate')}
{details.get('email', '')}
{details.get('phone', '')}"""

# ============================================
# SKILL DEVELOPMENT
# ============================================
def analyze_skill_gap(resume_skills: List[str], job_description: str) -> Dict[str, List[str]]:
    """Compares resume skills with job requirements."""
    all_skills = {
        "python", "java", "c++", "javascript", "typescript", "go", "rust", "c#", "php", "ruby",
        "sql", "nosql", "mongodb", "postgresql", "mysql", "redis", "cassandra", "dynamodb",
        "ai", "ml", "machine learning", "deep learning", "nlp", "computer vision", 
        "pytorch", "tensorflow", "keras", "scikit-learn", "neural networks",
        "aws", "gcp", "azure", "docker", "kubernetes", "jenkins", "terraform", "ansible",
        "react", "angular", "vue", "node", "express", "django", "flask", "spring", "fastapi",
        "git", "ci/cd", "agile", "scrum", "devops", "tdd", "rest api", "graphql", "microservices",
        "spark", "hadoop", "kafka", "elasticsearch", "etl", "data engineering",
        "data analysis", "statistics", "data visualization", "tableau", "power bi", "big data",
        "unity", "game development", "mobile development", "swift", "kotlin", "react native",
        "html", "css", "web development", "frontend", "backend", "full stack",
        "data science", "git", "ci/cd", "agile", "scrum", "devops", "tdd", "rest api", "graphql", "microservices",
        "unreal engine", "augmented reality", "virtual reality"
    }
    
    job_lower = job_description.lower()
    resume_skills_lower = {skill.lower() for skill in resume_skills}
    
    required_skills = {skill.title() for skill in all_skills if skill in job_lower}
    missing_skills = list(required_skills - {skill.title() for skill in resume_skills_lower})
    
    return {"missing_skills": missing_skills[:10], "matched_skills": resume_skills}

def get_course_recommendations(skills: List[str]) -> List[Dict[str, Any]]:
    """Fetches course recommendations for a list of skills."""
    return [
        {
            "skill": skill,
            "youtube": search_youtube_courses(skill),
            "curated": get_curated_courses(skill)
        }
        for skill in skills[:5]
    ]

def search_youtube_courses(skill: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Searches YouTube for relevant educational videos."""
    params = {
        "part": "snippet",
        "q": f"{skill} tutorial complete course",
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
        "order": "relevance"
    }
    
    try:
        response = requests.get(YOUTUBE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return [
            {
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "platform": "YouTube"
            }
            for item in data.get("items", [])
        ]
    except requests.RequestException as e:
        print(f"Error fetching YouTube courses: {e}")
        return []

def get_curated_courses(skill: str) -> List[Dict[str, str]]:
    """Provides curated courses for common skills."""
    courses_db = {
        "python": [
            {"title": "Python for Everybody (Coursera)", "url": "https://www.coursera.org/specializations/python", "platform": "Coursera"},
            {"title": "Complete Python Bootcamp (Udemy)", "url": "https://www.udemy.com/course/complete-python-bootcamp/", "platform": "Udemy"}
        ],
        "java": [
            {"title": "Java Programming Masterclass (Udemy)", "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/", "platform": "Udemy"},
            {"title": "Object Oriented Java Programming (Coursera)", "url": "https://www.coursera.org/learn/object-oriented-java", "platform": "Coursera"}
        ],
        "javascript": [
            {"title": "JavaScript - The Complete Guide (Udemy)", "url": "https://www.udemy.com/course/javascript-the-complete-guide-2020-beginner-advanced/", "platform": "Udemy"},
            {"title": "Modern JavaScript (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "platform": "freeCodeCamp"}
        ],
        "machine learning": [
            {"title": "Machine Learning by Andrew Ng", "url": "https://www.coursera.org/learn/machine-learning", "platform": "Coursera"},
            {"title": "Fast.ai Practical Deep Learning", "url": "https://course.fast.ai/", "platform": "Fast.ai"}
        ],
        "deep learning": [
            {"title": "Deep Learning Specialization", "url": "https://www.coursera.org/specializations/deep-learning", "platform": "Coursera"},
            {"title": "Practical Deep Learning for Coders", "url": "https://course.fast.ai/", "platform": "Fast.ai"}
        ],
        "pytorch": [
            {"title": "PyTorch for Deep Learning (Udacity)", "url": "https://www.udacity.com/course/deep-learning-pytorch--ud188", "platform": "Udacity"},
            {"title": "PyTorch Official Tutorials", "url": "https://pytorch.org/tutorials/", "platform": "PyTorch"}
        ],
        "tensorflow": [
            {"title": "TensorFlow Developer Certificate", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice", "platform": "Coursera"},
            {"title": "TensorFlow 2.0 Complete Course", "url": "https://www.freecodecamp.org/news/massive-tensorflow-2-0-free-course/", "platform": "freeCodeCamp"}
        ],
        "aws": [
            {"title": "AWS Cloud Practitioner Essentials", "url": "https://www.coursera.org/learn/aws-cloud-practitioner-essentials", "platform": "Coursera"},
            {"title": "AWS Certified Solutions Architect", "url": "https://www.udemy.com/course/aws-certified-solutions-architect-associate/", "platform": "Udemy"}
        ],
        "docker": [
            {"title": "Docker for Beginners", "url": "https://www.udemy.com/course/docker-tutorial-for-devops-run-docker-containers/", "platform": "Udemy"},
            {"title": "Docker Official Documentation", "url": "https://docs.docker.com/get-started/", "platform": "Docker"}
        ],
        "kubernetes": [
            {"title": "Kubernetes for Beginners (Udemy)", "url": "https://www.udemy.com/course/learn-kubernetes/", "platform": "Udemy"},
            {"title": "Kubernetes Official Tutorials", "url": "https://kubernetes.io/docs/tutorials/", "platform": "Kubernetes"}
        ],
        "react": [
            {"title": "React - The Complete Guide (Udemy)", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "platform": "Udemy"},
            {"title": "React Official Tutorial", "url": "https://react.dev/learn", "platform": "React"}
        ],
        "angular": [
            {"title": "Angular - The Complete Guide (Udemy)", "url": "https://www.udemy.com/course/the-complete-guide-to-angular-2/", "platform": "Udemy"},
            {"title": "Angular Official Tutorial", "url": "https://angular.io/tutorial", "platform": "Angular"}
        ],
        "node": [
            {"title": "Node.js - The Complete Guide (Udemy)", "url": "https://www.udemy.com/course/nodejs-the-complete-guide/", "platform": "Udemy"},
            {"title": "Node.js Official Guides", "url": "https://nodejs.org/en/docs/guides/", "platform": "Node.js"}
        ],
        "sql": [
            {"title": "The Complete SQL Bootcamp (Udemy)", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "platform": "Udemy"},
            {"title": "SQL for Data Science (Coursera)", "url": "https://www.coursera.org/learn/sql-for-data-science", "platform": "Coursera"}
        ],
        "data science": [
            {"title": "Data Science Specialization (Coursera)", "url": "https://www.coursera.org/specializations/jhu-data-science", "platform": "Coursera"},
            {"title": "Python for Data Science (Udemy)", "url": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/", "platform": "Udemy"}
        ],
        "git": [
            {"title": "Git Complete: The Definitive Guide (Udemy)", "url": "https://www.udemy.com/course/git-complete/", "platform": "Udemy"},
            {"title": "Git Official Documentation", "url": "https://git-scm.com/doc", "platform": "Git"}
        ]
    }
    
    skill_lower = skill.lower()
    for key in courses_db:
        if key in skill_lower or skill_lower in key:
            return courses_db[key]
    
    return [{"title": f"{skill} Fundamentals", "url": f"https://www.google.com/search?q={skill}+course", "platform": "Search"}]

# ============================================
# INTERVIEW PREPARATION
# ============================================
def search_company_info(company_name: str) -> Dict[str, List[Dict[str, str]]]:
    """Gathers information about a company from various sources."""
    queries = {
        "news": f"{company_name} recent news 2024 2025",
        "culture": f"{company_name} work culture employee reviews glassdoor",
        "hiring": f"{company_name} hiring trends layoffs expansion",
        "overview": f"{company_name} company profile about mission values"
    }
    
    results: Dict[str, List[Dict[str, str]]] = {}
    
    for category, query in queries.items():
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 5,
            "gl": "in",
            "hl": "en"
        }
        
        try:
            response = requests.get(SERPAPI_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            results[category] = [
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", "")
                }
                for item in data.get("organic_results", [])[:3]
            ]
        except requests.RequestException as e:
            print(f"Error fetching {category} for {company_name}: {e}")
            results[category] = []
                
    return results

def get_common_interview_questions(job_title: str, company_name: str) -> List[Dict[str, str]]:
    """Finds common interview questions for a specific role and company."""
    query = f"{company_name} {job_title} interview questions experiences glassdoor leetcode"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 8,
        "gl": "in",
        "hl": "en"
    }
    
    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        return [
            {
                "source": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", "")
            }
            for item in data.get("organic_results", [])[:5]
        ]
    except requests.RequestException as e:
        print(f"Error fetching interview questions: {e}")
        return []

def generate_interview_brief(company_name: str, job_title: str, company_info: Dict[str, Any], interview_questions: List[Dict[str, str]]) -> str:
    """Generates a comprehensive interview brief using Gemini AI."""
    try:
        import google.generativeai as genai
        
        def format_items(items: List[Dict[str, str]]) -> str:
            """Helper to format list of items."""
            if not items:
                return "No information found"
            return "\n".join(f"- {item.get('title', 'N/A')}: {item.get('snippet', 'N/A')[:200]}" for item in items)

        news_summary = format_items(company_info.get('news', []))
        culture_summary = format_items(company_info.get('culture', []))
        hiring_summary = format_items(company_info.get('hiring', []))
        overview_summary = format_items(company_info.get('overview', []))
        questions_summary = format_items(interview_questions)

        prompt = f"""Create a comprehensive interview preparation brief for:

Company: {company_name}
Position: {job_title}

COMPANY INFORMATION:

Company Overview:
{overview_summary}

Recent News:
{news_summary}

Work Culture:
{culture_summary}

Hiring Trends:
{hiring_summary}

Interview Experiences:
{questions_summary}

Please provide a structured interview preparation guide with:

1. **Company Snapshot** (2-3 paragraphs summarizing what the company does and recent developments)

2. **Work Culture & Values** (what they value in employees based on the culture information)

3. **Recent News Impact** (how recent news might affect the interview conversation)

4. **Expected Interview Questions** (5-7 specific questions likely to be asked):
   - Technical questions for this role
   - Behavioral questions
   - Company-specific questions

5. **Interview Success Tips** (specific strategies for this company and role)

6. **Smart Questions to Ask** (5 intelligent questions based on company research)

Keep it professional, actionable, and well-structured."""
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        print(f"Error generating interview brief: {e}")
        import traceback
        traceback.print_exc()
        
        # Better fallback with actual data
        return f"""# Interview Preparation Brief

## Company: {company_name}
## Position: {job_title}

---

## Company Overview

{overview_summary if overview_summary != "No information found" else "Research the company's main products/services and mission statement before the interview."}

---

## Recent Company News

{news_summary if news_summary != "No information found" else "Check the company's press releases and news section on their website."}

**Why This Matters:** Recent news can be great conversation starters and shows you're genuinely interested.

---

## Work Culture Insights

{culture_summary if culture_summary != "No information found" else "Look up employee reviews on Glassdoor, Indeed, or LinkedIn to understand the work environment."}

**Key Takeaway:** Understand what the company values to tailor your responses accordingly.

---

## Expected Interview Questions

### Technical Questions
1. Explain your experience with [relevant technology stack]
2. Walk me through a challenging project you've completed
3. How do you approach debugging/problem-solving?
4. Describe your experience with [specific framework/tool mentioned in job description]

### Behavioral Questions
1. Tell me about a time you faced a difficult challenge at work
2. Describe a situation where you had to work with a difficult team member
3. Give an example of when you had to learn something new quickly
4. Tell me about a project you're particularly proud of

### Company-Specific Questions
1. Why do you want to work for {company_name}?
2. What do you know about our products/services?
3. Where do you see yourself contributing to our team?

---

## Interview Success Strategies

### Before the Interview
- ✅ Review the job description thoroughly
- ✅ Prepare 3-5 specific examples using STAR method
- ✅ Research the company's recent projects/news
- ✅ Prepare questions to ask the interviewer
- ✅ Test your tech setup (if remote)

### During the Interview
- ✅ Be specific with examples (use numbers/metrics when possible)
- ✅ Show enthusiasm for the role and company
- ✅ Ask clarifying questions if needed
- ✅ Take notes during the conversation
- ✅ Be honest about what you don't know

### After the Interview
- ✅ Send a thank-you email within 24 hours
- ✅ Reference specific topics discussed
- ✅ Reiterate your interest in the position

---

## Smart Questions to Ask Your Interviewer

1. **About the Role:**
   - "What does success look like in this position after 6 months?"
   - "What are the biggest challenges facing the team right now?"

2. **About the Team:**
   - "Can you tell me about the team structure and who I'd be working with?"
   - "What's the team's approach to professional development?"

3. **About the Company:**
   - "How has the company evolved in the past year, and where do you see it going?"
   - "What do you enjoy most about working here?"

4. **About Growth:**
   - "What opportunities are there for growth and advancement?"
   - "How does the company support continued learning?"

5. **Next Steps:**
   - "What are the next steps in the interview process?"
   - "When can I expect to hear back?"

---

## Additional Research Resources

{questions_summary if questions_summary != "No information found" else "Search for '[Company Name] interview questions' on Glassdoor and Leetcode for more insights."}

---

## Final Tips

🎯 **Be Yourself:** Authenticity is valued more than memorized answers

💡 **Show Curiosity:** Ask thoughtful questions that demonstrate your interest

🔍 **Do Your Homework:** Knowledge about the company goes a long way

⏰ **Be Punctual:** Join 5 minutes early (or arrive 10 minutes early for in-person)

😊 **Stay Positive:** Even when discussing challenges, focus on solutions and learnings

---

**Good luck with your interview at {company_name}!** 🚀
"""

def research_company_for_interview(company_name: str, job_title: str) -> Dict[str, Any]:
    """Complete company research pipeline for interview preparation."""
    print(f"Researching {company_name} for {job_title} position...")
    
    # Fetch company information
    company_info = search_company_info(company_name)
    
    # Fetch common interview questions
    interview_questions = get_common_interview_questions(job_title, company_name)
    
    # Generate AI brief
    ai_brief = generate_interview_brief(company_name, job_title, company_info, interview_questions)
    
    return {
        "company_name": company_name,
        "job_title": job_title,
        "company_info": company_info,
        "interview_questions": interview_questions,
        "ai_brief": ai_brief
    }

# ============================================
# TESTING FUNCTIONS (Optional)
# ============================================
if __name__ == "__main__":
    # Test skill extraction
    sample_text = "Experienced Python developer with skills in machine learning, TensorFlow, AWS, and React."
    skills = extract_resume_skills(sample_text)
    print(f"Extracted Skills: {skills}")
    
    # Test job search
    print("Testing job search...")
    jobs = search_jobs(["Python", "Machine Learning"], "India", 3)
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Link: {job['link']}")