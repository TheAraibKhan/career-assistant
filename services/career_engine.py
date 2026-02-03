"""Career progression engine - provides role data, skill requirements, and career paths."""

# Career roles database - realistic industry roles with progression
CAREER_DATABASE = {
    'backend': {
        'beginner': {
            'role': 'Junior Backend Engineer',
            'tier': 'beginner',
            'next_role': 'Backend Engineer',
            'time_to_ready_months': 3,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'Backend Engineer',
            'tier': 'junior',
            'next_role': 'Senior Backend Engineer',
            'time_to_ready_months': 6,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Senior Backend Engineer',
            'tier': 'intermediate',
            'next_role': 'Staff Backend Engineer',
            'time_to_ready_months': 12,
            'market_demand': 'Very High'
        },
        'senior': {
            'role': 'Staff Backend Engineer',
            'tier': 'senior',
            'next_role': 'Backend Engineering Manager',
            'time_to_ready_months': 18,
            'market_demand': 'High'
        },
        'lead': {
            'role': 'Backend Engineering Manager',
            'tier': 'lead',
            'next_role': 'Director of Engineering',
            'time_to_ready_months': 24,
            'market_demand': 'Medium'
        }
    },
    'frontend': {
        'beginner': {
            'role': 'Junior Frontend Engineer',
            'tier': 'beginner',
            'next_role': 'Frontend Engineer',
            'time_to_ready_months': 3,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'Frontend Engineer',
            'tier': 'junior',
            'next_role': 'Senior Frontend Engineer',
            'time_to_ready_months': 6,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Senior Frontend Engineer',
            'tier': 'intermediate',
            'next_role': 'Staff Frontend Engineer',
            'time_to_ready_months': 12,
            'market_demand': 'High'
        },
        'senior': {
            'role': 'Staff Frontend Engineer',
            'tier': 'senior',
            'next_role': 'Frontend Engineering Manager',
            'time_to_ready_months': 18,
            'market_demand': 'Medium'
        },
        'lead': {
            'role': 'Frontend Engineering Manager',
            'tier': 'lead',
            'next_role': 'Director of Engineering',
            'time_to_ready_months': 24,
            'market_demand': 'Medium'
        }
    },
    'fullstack': {
        'beginner': {
            'role': 'Junior Full-Stack Engineer',
            'tier': 'beginner',
            'next_role': 'Full-Stack Engineer',
            'time_to_ready_months': 4,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'Full-Stack Engineer',
            'tier': 'junior',
            'next_role': 'Senior Full-Stack Engineer',
            'time_to_ready_months': 8,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Senior Full-Stack Engineer',
            'tier': 'intermediate',
            'next_role': 'Staff Full-Stack Engineer',
            'time_to_ready_months': 14,
            'market_demand': 'High'
        },
        'senior': {
            'role': 'Staff Full-Stack Engineer',
            'tier': 'senior',
            'next_role': 'Engineering Manager',
            'time_to_ready_months': 20,
            'market_demand': 'Medium'
        },
        'lead': {
            'role': 'Engineering Manager',
            'tier': 'lead',
            'next_role': 'Director of Engineering',
            'time_to_ready_months': 24,
            'market_demand': 'Medium'
        }
    },
    'ml': {
        'beginner': {
            'role': 'ML Engineer Intern',
            'tier': 'beginner',
            'next_role': 'ML Engineer',
            'time_to_ready_months': 4,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'ML Engineer',
            'tier': 'junior',
            'next_role': 'Senior ML Engineer',
            'time_to_ready_months': 8,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Senior ML Engineer',
            'tier': 'intermediate',
            'next_role': 'Staff ML Engineer',
            'time_to_ready_months': 14,
            'market_demand': 'Very High'
        },
        'senior': {
            'role': 'Staff ML Engineer',
            'tier': 'senior',
            'next_role': 'ML Engineering Manager',
            'time_to_ready_months': 20,
            'market_demand': 'High'
        },
        'lead': {
            'role': 'ML Engineering Manager',
            'tier': 'lead',
            'next_role': 'Director of ML',
            'time_to_ready_months': 24,
            'market_demand': 'Medium'
        }
    },
    'nlp': {
        'beginner': {
            'role': 'NLP Engineer Intern',
            'tier': 'beginner',
            'next_role': 'NLP Engineer',
            'time_to_ready_months': 5,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'NLP Engineer',
            'tier': 'junior',
            'next_role': 'Senior NLP Engineer',
            'time_to_ready_months': 9,
            'market_demand': 'High'
        },
        'intermediate': {
            'role': 'Senior NLP Engineer',
            'tier': 'intermediate',
            'next_role': 'Staff NLP Engineer',
            'time_to_ready_months': 15,
            'market_demand': 'High'
        },
        'senior': {
            'role': 'Staff NLP Engineer',
            'tier': 'senior',
            'next_role': 'NLP Engineering Manager',
            'time_to_ready_months': 20,
            'market_demand': 'Medium'
        },
        'lead': {
            'role': 'NLP Engineering Manager',
            'tier': 'lead',
            'next_role': 'Director of NLP Research',
            'time_to_ready_months': 24,
            'market_demand': 'Low'
        }
    },
    'data': {
        'beginner': {
            'role': 'Data Analyst',
            'tier': 'beginner',
            'next_role': 'Junior Data Scientist',
            'time_to_ready_months': 4,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'Junior Data Scientist',
            'tier': 'junior',
            'next_role': 'Data Scientist',
            'time_to_ready_months': 6,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Data Scientist',
            'tier': 'intermediate',
            'next_role': 'Senior Data Scientist',
            'time_to_ready_months': 12,
            'market_demand': 'High'
        },
        'senior': {
            'role': 'Senior Data Scientist',
            'tier': 'senior',
            'next_role': 'Data Science Manager',
            'time_to_ready_months': 18,
            'market_demand': 'Medium'
        },
        'lead': {
            'role': 'Data Science Manager',
            'tier': 'lead',
            'next_role': 'Director of Data',
            'time_to_ready_months': 24,
            'market_demand': 'Medium'
        }
    },
    'ai': {
        'beginner': {
            'role': 'AI Engineer Intern',
            'tier': 'beginner',
            'next_role': 'AI Engineer',
            'time_to_ready_months': 5,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'AI Engineer',
            'tier': 'junior',
            'next_role': 'Senior AI Engineer',
            'time_to_ready_months': 8,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Senior AI Engineer',
            'tier': 'intermediate',
            'next_role': 'Staff AI Engineer',
            'time_to_ready_months': 14,
            'market_demand': 'Very High'
        },
        'senior': {
            'role': 'Staff AI Engineer',
            'tier': 'senior',
            'next_role': 'AI Engineering Manager',
            'time_to_ready_months': 20,
            'market_demand': 'High'
        },
        'lead': {
            'role': 'AI Engineering Manager',
            'tier': 'lead',
            'next_role': 'Director of AI',
            'time_to_ready_months': 24,
            'market_demand': 'Medium'
        }
    },
    'mlops': {
        'beginner': {
            'role': 'MLOps Engineer Intern',
            'tier': 'beginner',
            'next_role': 'MLOps Engineer',
            'time_to_ready_months': 4,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'MLOps Engineer',
            'tier': 'junior',
            'next_role': 'Senior MLOps Engineer',
            'time_to_ready_months': 8,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Senior MLOps Engineer',
            'tier': 'intermediate',
            'next_role': 'Staff MLOps Engineer',
            'time_to_ready_months': 14,
            'market_demand': 'High'
        },
        'senior': {
            'role': 'Staff MLOps Engineer',
            'tier': 'senior',
            'next_role': 'MLOps Engineering Manager',
            'time_to_ready_months': 20,
            'market_demand': 'Medium'
        },
        'lead': {
            'role': 'MLOps Engineering Manager',
            'tier': 'lead',
            'next_role': 'Director of MLOps',
            'time_to_ready_months': 24,
            'market_demand': 'Low'
        }
    },
    'data_engineering': {
        'beginner': {
            'role': 'Data Engineering Intern',
            'tier': 'beginner',
            'next_role': 'Data Engineer',
            'time_to_ready_months': 4,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'Data Engineer',
            'tier': 'junior',
            'next_role': 'Senior Data Engineer',
            'time_to_ready_months': 8,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Senior Data Engineer',
            'tier': 'intermediate',
            'next_role': 'Staff Data Engineer',
            'time_to_ready_months': 14,
            'market_demand': 'High'
        },
        'senior': {
            'role': 'Staff Data Engineer',
            'tier': 'senior',
            'next_role': 'Data Engineering Manager',
            'time_to_ready_months': 20,
            'market_demand': 'Medium'
        },
        'lead': {
            'role': 'Data Engineering Manager',
            'tier': 'lead',
            'next_role': 'Director of Data Engineering',
            'time_to_ready_months': 24,
            'market_demand': 'Medium'
        }
    },
    'design': {
        'beginner': {
            'role': 'Junior Product Designer',
            'tier': 'beginner',
            'next_role': 'Product Designer',
            'time_to_ready_months': 4,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'Product Designer',
            'tier': 'junior',
            'next_role': 'Senior Product Designer',
            'time_to_ready_months': 8,
            'market_demand': 'High'
        },
        'intermediate': {
            'role': 'Senior Product Designer',
            'tier': 'intermediate',
            'next_role': 'Lead Designer',
            'time_to_ready_months': 12,
            'market_demand': 'High'
        },
        'senior': {
            'role': 'Lead Designer',
            'tier': 'senior',
            'next_role': 'Design Manager',
            'time_to_ready_months': 18,
            'market_demand': 'Medium'
        },
        'lead': {
            'role': 'Design Manager',
            'tier': 'lead',
            'next_role': 'Director of Design',
            'time_to_ready_months': 24,
            'market_demand': 'Low'
        }
    },
    'product': {
        'beginner': {
            'role': 'Associate Product Manager',
            'tier': 'beginner',
            'next_role': 'Product Manager',
            'time_to_ready_months': 3,
            'market_demand': 'High'
        },
        'junior': {
            'role': 'Product Manager',
            'tier': 'junior',
            'next_role': 'Senior Product Manager',
            'time_to_ready_months': 6,
            'market_demand': 'Very High'
        },
        'intermediate': {
            'role': 'Senior Product Manager',
            'tier': 'intermediate',
            'next_role': 'Principal Product Manager',
            'time_to_ready_months': 12,
            'market_demand': 'High'
        },
        'senior': {
            'role': 'Principal Product Manager',
            'tier': 'senior',
            'next_role': 'Director of Product',
            'time_to_ready_months': 18,
            'market_demand': 'Medium'
        },
        'lead': {
            'role': 'Director of Product',
            'tier': 'lead',
            'next_role': 'VP of Product',
            'time_to_ready_months': 24,
            'market_demand': 'Low'
        }
    }
}

# Core skills by specialization - realistic and prioritized
ROLE_SKILL_REQUIREMENTS = {
    'Backend Engineer': {
        'core': ['Python', 'Go', 'Java', 'Node.js', 'Databases', 'API Design', 'System Design'],
        'supporting': ['Docker', 'CI/CD', 'SQL Optimization', 'Caching'],
        'optional': ['Kubernetes', 'Message Queues']
    },
    'Frontend Engineer': {
        'core': ['JavaScript', 'React', 'CSS', 'HTML', 'State Management', 'Responsive Design'],
        'supporting': ['TypeScript', 'Testing', 'Performance Optimization', 'Accessibility'],
        'optional': ['Vue', 'Svelte', 'Web Animation']
    },
    'Full-Stack Engineer': {
        'core': ['JavaScript/TypeScript', 'Frontend Framework', 'Backend Language', 'Database', 'APIs'],
        'supporting': ['Docker', 'Version Control', 'Testing', 'Deployment'],
        'optional': ['Cloud Platforms', 'Microservices']
    },
    'ML Engineer': {
        'core': ['Python', 'TensorFlow', 'PyTorch', 'Statistics', 'Data Structures'],
        'supporting': ['Scikit-learn', 'Feature Engineering', 'Model Evaluation', 'SQL'],
        'optional': ['Distributed Training', 'MLOps Basics']
    },
    'NLP Engineer': {
        'core': ['Python', 'NLP Frameworks', 'Transformers', 'Deep Learning', 'Statistics'],
        'supporting': ['NLTK', 'Spacy', 'Text Preprocessing', 'Language Models'],
        'optional': ['Prompt Engineering', 'Fine-tuning']
    },
    'Data Scientist': {
        'core': ['Python', 'SQL', 'Statistics', 'Data Analysis', 'Pandas', 'NumPy'],
        'supporting': ['Scikit-learn', 'Visualization', 'A/B Testing', 'Machine Learning'],
        'optional': ['Deep Learning', 'Big Data Platforms']
    },
    'AI Engineer': {
        'core': ['Python', 'Machine Learning', 'Deep Learning', 'System Design', 'Statistics'],
        'supporting': ['Large Language Models', 'Vector Databases', 'Prompt Engineering'],
        'optional': ['Reinforcement Learning', 'Computer Vision']
    },
    'MLOps Engineer': {
        'core': ['Python', 'Docker', 'Kubernetes', 'CI/CD', 'ML Frameworks'],
        'supporting': ['Cloud Platforms', 'Monitoring', 'Model Registry', 'Infrastructure'],
        'optional': ['Terraform', 'Advanced Kubernetes']
    },
    'Data Engineer': {
        'core': ['SQL', 'Python', 'Data Pipelines', 'ETL', 'Databases'],
        'supporting': ['Spark', 'Hadoop', 'Cloud Data', 'Schema Design'],
        'optional': ['Stream Processing', 'Data Lakes']
    },
    'Product Designer': {
        'core': ['Figma', 'User Research', 'Wireframing', 'Prototyping', 'Visual Design'],
        'supporting': ['Usability Testing', 'Design Systems', 'UI Design', 'Interaction Design'],
        'optional': ['Animation', 'Video Editing']
    },
    'Product Manager': {
        'core': ['Product Strategy', 'Analytics', 'User Understanding', 'Roadmap Planning'],
        'supporting': ['Data Analysis', 'Communication', 'Project Management', 'Metrics'],
        'optional': ['Financial Modeling', 'Technical Depth']
    }
}


def get_career_recommendation(interest, level):
    """Get detailed career recommendation."""
    interest = interest.lower().strip()
    level = level.lower().strip()
    
    # Normalize level names if needed
    level_map = {
        'advanced': 'senior',
        'expert': 'lead'
    }
    level = level_map.get(level, level)
    
    if interest not in CAREER_DATABASE or level not in CAREER_DATABASE[interest]:
        return None
    
    return CAREER_DATABASE[interest][level]


def get_role_skills(role):
    """Get skill requirements for a role."""
    return ROLE_SKILL_REQUIREMENTS.get(role, {})


def get_all_roles():
    """Get all available roles."""
    roles = []
    for interest, levels in CAREER_DATABASE.items():
        for level, data in levels.items():
            roles.append({
                'interest': interest,
                'level': level,
                **data
            })
    return roles


def calculate_career_confidence(interest, level, user_skills):
    """Calculate confidence score based on interest, level, and user skills."""
    base_confidence = {
        'beginner': 55,
        'junior': 70,
        'intermediate': 80,
        'advanced': 85,
        'expert': 90
    }
    
    score = base_confidence.get(level, 50)
    
    # Adjust based on skill match
    if user_skills:
        role_data = get_career_recommendation(interest, level)
        if role_data and 'role' in role_data:
            role_skills = get_role_skills(role_data['role'])
            matched_skills = len([s for s in user_skills if any(
                s.lower() in skill.lower() for skill in 
                role_skills.get('core', []) + role_skills.get('technical', [])
            )])
            
            if matched_skills > 0:
                adjustment = min(matched_skills * 2, 10)
                score = min(score + adjustment, 95)
    
    return score


def get_career_guidance(interest, level, user_skills):
    """Generate detailed career guidance for a user."""
    career_rec = get_career_recommendation(interest, level)
    
    if not career_rec:
        return None
    
    role = career_rec['role']
    role_skills = get_role_skills(role)
    
    # Determine interest name for display
    interest_names = {
        'backend': 'Backend Engineering',
        'frontend': 'Frontend Engineering',
        'fullstack': 'Full-Stack Engineering',
        'ml': 'Machine Learning Engineering',
        'nlp': 'NLP Engineering',
        'data': 'Data Science',
        'ai': 'AI Engineering',
        'mlops': 'MLOps Engineering',
        'data_engineering': 'Data Engineering',
        'design': 'Product Design',
        'product': 'Product Management'
    }
    
    # Career journey descriptions - now with new levels
    career_journeys = {
        'ai': {
            'beginner': 'Start by mastering Python, fundamental ML concepts, and working on beginner-friendly projects.',
            'junior': 'Develop production-ready ML models, learn system design, and contribute to real projects.',
            'intermediate': 'Lead ML projects, optimize models for performance, implement advanced techniques.',
            'senior': 'Architect large-scale systems, mentor engineers, and drive innovation.',
            'lead': 'Define ML strategy, lead teams, and shape organizational ML capabilities.'
        },
        'backend': {
            'beginner': 'Master programming fundamentals, software development practices, and build small projects.',
            'junior': 'Build features independently, learn system design, develop professional standards.',
            'intermediate': 'Design scalable systems, lead feature development, mentor junior developers.',
            'senior': 'Architect complex systems, influence technical strategy, lead teams.',
            'lead': 'Define technical direction, lead architecture, drive engineering excellence.'
        },
        'data': {
            'beginner': 'Learn data manipulation, SQL, visualization, and statistical analysis.',
            'junior': 'Build predictive models, conduct analysis, and create insights.',
            'intermediate': 'Lead analytics initiatives, design models, and drive strategy.',
            'senior': 'Manage teams, shape ML strategy, deliver critical insights.',
            'lead': 'Lead data organization, define strategy, drive transformation.'
        },
        'design': {
            'beginner': 'Master design fundamentals, learn tools, and build a portfolio.',
            'junior': 'Design user-centered experiences, conduct research, deliver designs.',
            'intermediate': 'Lead design systems, mentor designers, shape strategy.',
            'senior': 'Direct design vision, lead collaboration, drive excellence.',
            'lead': 'Define strategy, lead culture, drive innovation.'
        },
        'product': {
            'beginner': 'Learn business fundamentals, market dynamics, and strategic thinking.',
            'junior': 'Manage features, conduct research, drive decisions.',
            'intermediate': 'Lead strategy, manage cross-functional teams, drive growth.',
            'senior': 'Own vision, lead initiatives, drive company impact.',
            'lead': 'Shape direction, lead transformation, drive market leadership.'
        },
        'frontend': {
            'beginner': 'Master HTML, CSS, JavaScript fundamentals and build projects.',
            'junior': 'Build interactive features, learn frameworks, develop professional code.',
            'intermediate': 'Design system components, lead frontend architecture, mentor.',
            'senior': 'Define frontend strategy, optimize performance, lead teams.',
            'lead': 'Define engineering direction, drive technical excellence.'
        },
        'fullstack': {
            'beginner': 'Learn both frontend and backend fundamentals, build full projects.',
            'junior': 'Build end-to-end features, learn system design.',
            'intermediate': 'Lead full-stack projects, optimize architecture.',
            'senior': 'Architect systems, mentor teams, drive strategy.',
            'lead': 'Define technical direction, lead organization.'
        },
        'ml': {
            'beginner': 'Master Python, ML fundamentals, work on projects.',
            'junior': 'Build production models, learn pipelines.',
            'intermediate': 'Lead projects, implement advanced techniques.',
            'senior': 'Architect systems, mentor teams.',
            'lead': 'Define strategy, shape capabilities.'
        },
        'nlp': {
            'beginner': 'Learn NLP fundamentals, language models.',
            'junior': 'Build NLP systems, solve problems.',
            'intermediate': 'Lead NLP projects, mentor.',
            'senior': 'Architect NLP systems, lead teams.',
            'lead': 'Define NLP strategy.'
        },
        'mlops': {
            'beginner': 'Learn deployment, monitoring, CI/CD.',
            'junior': 'Deploy models, manage pipelines.',
            'intermediate': 'Design ML infrastructure, mentor.',
            'senior': 'Lead MLOps strategy, architect systems.',
            'lead': 'Define organizational ML infrastructure.'
        },
        'data_engineering': {
            'beginner': 'Learn data pipelines, SQL, ETL.',
            'junior': 'Build data systems, manage pipelines.',
            'intermediate': 'Design architectures, mentor.',
            'senior': 'Lead data infrastructure, shape strategy.',
            'lead': 'Define data engineering direction.'
        }
    }
    
    # Why this role guidance
    role_guidance = {
        'ai': 'AI engineering is rapidly growing with high demand for engineers who can build and deploy AI systems effectively.',
        'backend': 'Backend engineering is fundamental to all software systems and remains in high demand with strong career growth.',
        'frontend': 'Frontend engineering creates the user interface and experience that drives business value.',
        'fullstack': 'Full-stack engineers can build complete systems and are valued for their broad capabilities.',
        'data': 'Data science combines statistics and programming to drive insights and inform decisions.',
        'design': 'Product design is critical for creating exceptional user experiences.',
        'product': 'Product management sits at the intersection of technology, business, and user needs.',
        'ml': 'Machine learning engineering builds and deploys models that solve real problems.',
        'nlp': 'NLP engineering addresses language understanding challenges across many industries.',
        'mlops': 'MLOps bridges the gap between ML research and production deployments.',
        'data_engineering': 'Data engineering builds the infrastructure that powers analytics and ML.'
    }
    
    # Timeline to next level
    timelines = {
        'beginner': '3-6 months with consistent learning and project work',
        'junior': '6-12 months with focused skill development and real-world experience',
        'intermediate': '12-18 months of specialized experience and leadership growth',
        'senior': '18-24 months of strategic contributions and team leadership',
        'lead': '24+ months of organizational impact and leadership'
    }
    
    matched_skills = []
    missing_skills = []
    
    if role_skills:
        core_skills = role_skills.get('core', [])
        supporting_skills = role_skills.get('supporting', [])
        optional_skills = role_skills.get('optional', [])
        all_required = core_skills + supporting_skills + optional_skills
        
        for skill in all_required:
            if any(s.lower() in skill.lower() or skill.lower() in s.lower() for s in user_skills):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
    
    return {
        'role': role,
        'interest': interest_names.get(interest, interest),
        'level': level.capitalize(),
        'salary': career_rec['avg_salary'],
        'market_demand': career_rec['market_demand'],
        'next_role': career_rec.get('next_role'),
        'journey_description': career_journeys.get(interest, {}).get(level, ''),
        'why_this_role': role_guidance.get(interest, ''),
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'time_to_next_level': timelines.get(level, ''),
        'skill_requirements': role_skills,
        'confidence': calculate_career_confidence(interest, level, user_skills),
        'roadmap': get_career_roadmap(interest, level, matched_skills, missing_skills)
    }


def get_career_roadmap(interest, level, matched_skills, missing_skills):
    """Generate a 3-4, 6-9, 12-15 month career development roadmap."""
    
    roadmaps = {
        'ai': {
            'beginner': {
                'month_3_4': [
                    'Complete Python fundamentals and ML basics course',
                    'Build 2-3 beginner ML projects (iris dataset, house price prediction)',
                    'Learn numpy, pandas, scikit-learn libraries',
                    'Start contributing to open-source ML projects'
                ],
                'month_6_9': [
                    'Complete intermediate ML course (neural networks, deep learning)',
                    'Build a real-world project using deep learning',
                    'Learn TensorFlow or PyTorch',
                    'Publish 1-2 ML project writeups on Medium/Blog'
                ],
                'month_12_15': [
                    'Develop portfolio with 4-5 production-ready projects',
                    'Contribute meaningfully to open-source ML projects',
                    'Begin job search for ML Engineer/Data Science roles',
                    'Prepare for ML interviews and system design questions'
                ]
            },
            'junior': {
                'month_3_4': [
                    'Master advanced ML techniques (ensemble methods, hyperparameter tuning)',
                    'Learn production ML practices and MLOps basics',
                    'Develop 1-2 projects with real datasets and deployment',
                    'Study cloud ML platforms (Google Cloud, AWS SageMaker)'
                ],
                'month_6_9': [
                    'Implement ML pipeline for production use',
                    'Learn model monitoring and drift detection',
                    'Deploy ML model to production environment',
                    'Mentor 1-2 junior developers/interns'
                ],
                'month_12_15': [
                    'Lead ML project from conception to deployment',
                    'Optimize model performance for production scale',
                    'Document best practices and share knowledge',
                    'Target senior ML Engineer role'
                ]
            },
            'intermediate': {
                'month_3_4': [
                    'Architect large-scale ML systems',
                    'Deep dive into advanced techniques (NLP, Computer Vision, RL)',
                    'Design scalable data pipelines',
                    'Lead cross-functional ML projects'
                ],
                'month_6_9': [
                    'Implement complex ML solutions for business problems',
                    'Optimize models for latency and efficiency',
                    'Build ML platform and infrastructure',
                    'Mentor and lead team of engineers'
                ],
                'month_12_15': [
                    'Shape ML strategy for organization',
                    'Drive innovation in new ML domains',
                    'Present research or technical talks',
                    'Target Lead/Senior ML role'
                ]
            }
        },
        'tech': {
            'beginner': {
                'month_3_4': [
                    'Master a programming language (Python, JavaScript, or Go)',
                    'Learn data structures and algorithms fundamentals',
                    'Build 2-3 small projects (todo app, calculator, API)',
                    'Study web development basics (HTML, CSS, JavaScript)'
                ],
                'month_6_9': [
                    'Learn framework (Django, React, or Spring)',
                    'Understand database concepts and SQL',
                    'Build a full-stack project with frontend + backend',
                    'Contribute to open-source projects'
                ],
                'month_12_15': [
                    'Develop portfolio with 3-4 complete projects',
                    'Learn version control and CI/CD basics',
                    'Prepare for technical interviews',
                    'Target Junior Developer role'
                ]
            },
            'junior': {
                'month_3_4': [
                    'Master system design fundamentals',
                    'Learn testing and code quality practices',
                    'Develop 1-2 features end-to-end',
                    'Understand microservices architecture'
                ],
                'month_6_9': [
                    'Lead feature development independently',
                    'Optimize application performance',
                    'Implement caching and database optimization',
                    'Mentor junior developers'
                ],
                'month_12_15': [
                    'Design scalable system architecture',
                    'Lead cross-functional projects',
                    'Contribute to technical strategy',
                    'Target Mid-level Developer role'
                ]
            }
        },
        'data': {
            'beginner': {
                'month_3_4': [
                    'Master SQL and relational databases',
                    'Learn data visualization (Tableau, Power BI, Matplotlib)',
                    'Build 2-3 data analysis projects',
                    'Study Python for data analysis (pandas, numpy)'
                ],
                'month_6_9': [
                    'Learn statistical analysis and hypothesis testing',
                    'Build predictive models with scikit-learn',
                    'Create interactive dashboards',
                    'Analyze real-world datasets'
                ],
                'month_12_15': [
                    'Develop 3-4 complete analytics projects',
                    'Master data storytelling and presentation',
                    'Build business intelligence solutions',
                    'Target Data Analyst role'
                ]
            },
            'junior': {
                'month_3_4': [
                    'Learn advanced statistical methods',
                    'Master machine learning for predictions',
                    'Develop 1-2 ML models with real data',
                    'Learn data pipeline design'
                ],
                'month_6_9': [
                    'Lead analytics project from planning to insights',
                    'Optimize data workflows and ETL processes',
                    'Mentor analysts on technical skills',
                    'Present insights to stakeholders'
                ],
                'month_12_15': [
                    'Design analytics strategy and roadmap',
                    'Lead cross-functional analytics initiatives',
                    'Drive business impact through data',
                    'Target Senior Data Scientist role'
                ]
            }
        },
        'design': {
            'beginner': {
                'month_3_4': [
                    'Master Figma and design tools',
                    'Study design fundamentals (typography, color, layout)',
                    'Complete 2-3 UI design projects',
                    'Learn UX research basics'
                ],
                'month_6_9': [
                    'Conduct user research and interviews',
                    'Create wireframes and prototypes',
                    'Design responsive interfaces',
                    'Build design system components'
                ],
                'month_12_15': [
                    'Develop strong portfolio with 4-5 projects',
                    'Master interaction design',
                    'Understand accessibility (A11y) standards',
                    'Target UI/UX Designer role'
                ]
            },
            'junior': {
                'month_3_4': [
                    'Lead design for product features',
                    'Conduct user testing and iterate',
                    'Learn product strategy basics',
                    'Build design systems'
                ],
                'month_6_9': [
                    'Own end-to-end design of features',
                    'Mentor junior designers',
                    'Establish design best practices',
                    'Drive design decisions with data'
                ],
                'month_12_15': [
                    'Lead product design strategy',
                    'Influence company design direction',
                    'Build strong design team culture',
                    'Target Senior Designer/Design Lead role'
                ]
            }
        },
        'business': {
            'beginner': {
                'month_3_4': [
                    'Learn product management fundamentals',
                    'Study market research and competitive analysis',
                    'Conduct 2-3 user interviews',
                    'Understand product metrics and KPIs'
                ],
                'month_6_9': [
                    'Lead product feature from idea to launch',
                    'Build product roadmap',
                    'Analyze user data and identify opportunities',
                    'Present product strategy to stakeholders'
                ],
                'month_12_15': [
                    'Own product strategy and direction',
                    'Manage cross-functional teams',
                    'Launch products successfully',
                    'Target Product Manager role'
                ]
            },
            'junior': {
                'month_3_4': [
                    'Lead product initiative independently',
                    'Master analytics and data interpretation',
                    'Conduct market research and competitive analysis',
                    'Mentor product associates'
                ],
                'month_6_9': [
                    'Own product P&L (profit and loss)',
                    'Launch multiple successful products',
                    'Build strong cross-functional relationships',
                    'Influence company product strategy'
                ],
                'month_12_15': [
                    'Lead product strategy for business unit',
                    'Mentor and build product team',
                    'Drive significant business growth',
                    'Target Senior PM/Principal PM role'
                ]
            }
        }
    }
    
    # Return roadmap or empty dict if not found
    return roadmaps.get(interest, {}).get(level, {
        'month_3_4': ['Continue learning and skill development'],
        'month_6_9': ['Apply skills in real-world projects'],
        'month_12_15': ['Target next career level']
    })