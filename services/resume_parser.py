"""Resume parsing and skill extraction service."""
import os
import hashlib
import json
from datetime import datetime

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from database.db import get_db


def extract_text_from_pdf(file_path):
    """Extract text from PDF file."""
    if not PDF_AVAILABLE:
        return None
    
    try:
        text = []
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None


def extract_text_from_docx(file_path):
    """Extract text from DOCX file."""
    if not DOCX_AVAILABLE:
        return None
    
    try:
        doc = Document(file_path)
        text = [para.text for para in doc.paragraphs]
        return '\n'.join(text)
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return None


def extract_text_from_txt(file_path):
    """Extract text from TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"TXT extraction error: {e}")
        return None


def extract_skills_from_text(text, skill_database=None):
    """Extract skills from resume text using keyword matching with fuzzy detection."""
    if not text:
        return []
    
    # Comprehensive skill database with variations
    if skill_database is None:
        skill_database = {
            'Programming': [
                ('Python', ['python', 'py']),
                ('Java', ['java', 'j2ee']),
                ('JavaScript', ['javascript', 'js', 'ecmascript']),
                ('TypeScript', ['typescript', 'ts']),
                ('C++', ['c++', 'cpp']),
                ('C#', ['c#', 'csharp']),
                ('Go', ['golang', 'go']),
                ('Rust', ['rust']),
                ('PHP', ['php']),
                ('Ruby', ['ruby']),
                ('Swift', ['swift']),
                ('Kotlin', ['kotlin']),
                ('R', ['r language', ' r ']),
                ('Scala', ['scala']),
                ('Perl', ['perl']),
            ],
            'Web Development': [
                ('HTML', ['html', 'html5']),
                ('CSS', ['css', 'css3', 'scss']),
                ('React', ['react', 'react.js', 'reactjs']),
                ('Vue', ['vue', 'vuejs', 'vue.js']),
                ('Angular', ['angular', 'angularjs']),
                ('Node.js', ['node.js', 'nodejs', 'node']),
                ('Express', ['express', 'expressjs']),
                ('Django', ['django']),
                ('Flask', ['flask']),
                ('ASP.NET', ['asp.net', 'aspnet']),
                ('GraphQL', ['graphql']),
                ('REST API', ['rest api', 'rest', 'restful']),
                ('WebSockets', ['websocket', 'websockets']),
            ],
            'Data & Analytics': [
                ('SQL', ['sql', 'mysql', 'postgres']),
                ('Python', ['python']),
                ('R', ['r language', ' r ']),
                ('Pandas', ['pandas']),
                ('NumPy', ['numpy']),
                ('Matplotlib', ['matplotlib']),
                ('Tableau', ['tableau']),
                ('Power BI', ['power bi', 'powerbi']),
                ('Excel', ['excel', 'vba']),
                ('Spark', ['spark', 'pyspark', 'apache spark']),
                ('Hadoop', ['hadoop']),
                ('Kafka', ['kafka']),
            ],
            'Cloud & DevOps': [
                ('AWS', ['aws', 'amazon web services', 'ec2', 's3', 'lambda']),
                ('Azure', ['azure', 'microsoft azure']),
                ('GCP', ['gcp', 'google cloud']),
                ('Docker', ['docker']),
                ('Kubernetes', ['kubernetes', 'k8s']),
                ('Jenkins', ['jenkins']),
                ('CI/CD', ['ci/cd', 'continuous integration', 'continuous deployment']),
                ('Linux', ['linux', 'unix']),
                ('Git', ['git', 'github', 'gitlab', 'bitbucket']),
                ('Terraform', ['terraform']),
                ('Ansible', ['ansible']),
            ],
            'ML & AI': [
                ('Machine Learning', ['machine learning', 'ml']),
                ('Deep Learning', ['deep learning']),
                ('NLP', ['nlp', 'natural language processing']),
                ('Computer Vision', ['computer vision', 'cv']),
                ('TensorFlow', ['tensorflow']),
                ('PyTorch', ['pytorch']),
                ('Keras', ['keras']),
                ('Scikit-learn', ['scikit-learn', 'sklearn']),
                ('OpenAI', ['openai', 'gpt']),
                ('LLM', ['llm', 'large language model']),
            ],
            'Databases': [
                ('MySQL', ['mysql']),
                ('PostgreSQL', ['postgresql', 'postgres', 'psql']),
                ('MongoDB', ['mongodb', 'mongo']),
                ('Redis', ['redis']),
                ('Cassandra', ['cassandra']),
                ('Oracle', ['oracle']),
                ('DynamoDB', ['dynamodb']),
                ('Elasticsearch', ['elasticsearch']),
                ('SQLite', ['sqlite']),
            ],
            'Soft Skills': [
                ('Leadership', ['leadership', 'leading', 'team lead']),
                ('Communication', ['communication', 'communicating']),
                ('Project Management', ['project management', 'pm']),
                ('Agile', ['agile', 'scrum']),
                ('Problem Solving', ['problem solving', 'problem-solving']),
                ('Teamwork', ['teamwork', 'team work', 'collaboration']),
                ('Critical Thinking', ['critical thinking', 'analytical']),
                ('Creativity', ['creative', 'innovation']),
            ]
        }
    
    text_lower = text.lower()
    extracted_skills = {}
    
    for category, skills in skill_database.items():
        for skill_name, variations in skills:
            for variation in variations:
                # Use word boundaries for better matching
                import re
                # Match whole words or skill mentions (with word boundaries or punctuation)
                pattern = r'\b' + re.escape(variation) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    if skill_name not in extracted_skills:
                        extracted_skills[skill_name] = True
                    break  # Found this skill, no need to check other variations
    
    return sorted(list(extracted_skills.keys()))


def parse_resume(file_path):
    """Parse resume file and extract structured data."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Extract text based on file type
    text = None
    if ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif ext == '.docx':
        text = extract_text_from_docx(file_path)
    elif ext == '.txt':
        text = extract_text_from_txt(file_path)
    
    if not text:
        return None
    
    # Extract skills
    skills = extract_skills_from_text(text)
    
    # Simple heuristics for experience extraction
    experience_keywords = ['years', 'year', 'experience', 'worked', 'managed', 'led']
    has_experience = any(keyword in text.lower() for keyword in experience_keywords)
    
    # Education detection
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
    education = [keyword for keyword in education_keywords if keyword in text.lower()]
    
    return {
        'skills': skills,
        'has_experience': has_experience,
        'education': education,
        'text_length': len(text),
        'text': text,
        'extracted_at': datetime.utcnow().isoformat()
    }


def get_file_hash(file_path):
    """Generate hash of file for caching."""
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def cache_resume_parse(file_hash, parsed_data):
    """Cache parsed resume data."""
    db = get_db()
    
    db.execute(
        '''INSERT OR REPLACE INTO resume_cache 
           (file_hash, parsed_skills, parsed_experience, parsed_education, created_at)
           VALUES (?, ?, ?, ?, ?)''',
        (file_hash, 
         json.dumps(parsed_data.get('skills', [])),
         json.dumps({'has_experience': parsed_data.get('has_experience')}),
         json.dumps(parsed_data.get('education', [])),
         datetime.utcnow().isoformat())
    )
    db.commit()


def get_cached_parse(file_hash):
    """Retrieve cached parse result."""
    db = get_db()
    result = db.execute(
        'SELECT * FROM resume_cache WHERE file_hash = ?',
        (file_hash,)
    ).fetchone()
    
    if result:
        return {
            'skills': json.loads(result['parsed_skills']),
            'experience': json.loads(result['parsed_experience']),
            'education': json.loads(result['parsed_education'])
        }
    return None