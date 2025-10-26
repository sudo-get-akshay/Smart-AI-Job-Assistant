from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
from backend import (
    load_pdf_text,
    extract_resume_skills,
    search_jobs,
    generate_cover_letter,
    analyze_skill_gap,
    get_course_recommendations,
    research_company_for_interview
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production-12345'  # ✅ ADDED
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # ✅ ADDED

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    print("\n" + "="*60)
    print("📄 RESUME UPLOAD")
    print("="*60)
    
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            print(f"✓ File saved: {filename}")
            
            # Extract text and skills
            resume_text = load_pdf_text(filepath)
            print(f"✓ Text extracted: {len(resume_text)} chars")
            
            skills = extract_resume_skills(resume_text)
            print(f"✓ Skills found: {skills}")
            
            # Store in Flask session (persistent across requests)
            session['resume_text'] = resume_text
            session['skills'] = skills
            session['filename'] = filename
            session['session_id'] = filename
            session.permanent = True
            
            print(f"✓ Session created and stored")
            print("="*60 + "\n")
            
            return jsonify({
                'success': True,
                'session_id': filename,
                'filename': filename,
                'skills': skills
            })
        
        return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/search-jobs', methods=['POST'])
def search_jobs_api():
    try:
        data = request.get_json()
        skills = data.get('skills', [])  # This is likely a list
        location = data.get('location', 'India')
        limit = data.get('limit', 8)
        
        # ✅ Add debug print
        print(f"📥 Received skills: {type(skills)} - {skills}")
        print(f"📥 Location: {location}")
        
        # Call backend function (now handles both list and dict)
        jobs = search_jobs(skills, location, limit)
        
        return jsonify({
            'success': True,
            'jobs': jobs
        })
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter_api():
    print("\n" + "="*60)
    print("✉️  COVER LETTER GENERATION")
    print("="*60)
    
    try:
        # Parse request
        data = request.json
        if not data:
            print("✗ No JSON data received")
            return jsonify({'error': 'Invalid request format'}), 400
        
        job = data.get('job')
        
        print(f"Job provided: {job is not None}")
        
        # Validate job data
        if not job:
            print("✗ Missing job data")
            return jsonify({'error': 'Job data is required'}), 400
        
        # Get resume text from session
        resume_text = session.get('resume_text')
        if not resume_text:
            print("✗ No resume text in session")
            return jsonify({'error': 'Session expired. Please upload resume again.'}), 400
        
        print(f"✓ Resume text length: {len(resume_text)} chars")
        print(f"✓ Job: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
        
        # Generate cover letter
        print("Generating cover letter...")
        letter = generate_cover_letter(resume_text, job)
        
        print(f"✓ Cover letter generated ({len(letter)} chars)")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'cover_letter': letter
        })
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-skills', methods=['POST'])
def analyze_skills_api():
    try:
        data = request.json
        job_description = data.get('job_description')
        
        skills = session.get('skills')
        if not skills:
            return jsonify({'error': 'Session expired. Please upload resume again.'}), 400
        
        analysis = analyze_skill_gap(skills, job_description)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        print(f"Skill analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get-courses', methods=['POST'])
def get_courses_api():
    try:
        data = request.json
        skills = data.get('skills', [])
        
        courses = get_course_recommendations(skills)
        
        return jsonify({
            'success': True,
            'courses': courses
        })
    
    except Exception as e:
        print(f"Course recommendation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/research-company', methods=['POST'])
def research_company_api():
    try:
        data = request.json
        company_name = data.get('company_name')
        job_title = data.get('job_title')
        
        research = research_company_for_interview(company_name, job_title)
        
        return jsonify({
            'success': True,
            'research': research
        })
    
    except Exception as e:
        print(f"Company research error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AI JOB ASSISTANT STARTING")
    print("="*60)
    print(f"📁 Upload folder: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
    print(f"🌐 Server: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, threaded=True)