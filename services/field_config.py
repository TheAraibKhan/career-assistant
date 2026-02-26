"""
Field-Specific Resume Analysis Configuration

This module defines field-aware criteria for resume analysis.
Based on real recruiter expectations and ATS behavior.
"""

from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class FieldConfig:
    """Configuration for a specific career field."""
    name: str
    core_keywords: Set[str]
    supporting_keywords: Set[str]
    required_sections: List[str]
    impact_metrics: List[str]
    red_flags: List[str]
    experience_expectations: Dict[str, List[str]]


# Software Engineering - Backend
SOFTWARE_BACKEND = FieldConfig(
    name="Software Engineering (Backend)",
    core_keywords={
        # Languages
        'python', 'java', 'go', 'c++', 'c#', 'rust', 'scala', 'kotlin',
        # Frameworks
        'django', 'flask', 'spring', 'express', 'fastapi', 'node.js',
        # Databases
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        # Systems
        'api', 'rest', 'graphql', 'microservices', 'distributed systems',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd',
        # Practices
        'git', 'testing', 'agile', 'code review', 'system design'
    },
    supporting_keywords={
        'linux', 'bash', 'nginx', 'rabbitmq', 'kafka', 'grpc',
        'terraform', 'jenkins', 'github actions', 'monitoring',
        'logging', 'security', 'authentication', 'authorization'
    },
    required_sections=['experience', 'skills', 'education'],
    impact_metrics=[
        'requests per second', 'latency', 'throughput', 'uptime',
        'users', 'scale', 'performance improvement', 'cost reduction',
        'deployment frequency', 'bug reduction', 'test coverage'
    ],
    red_flags=[
        'no version control mentioned',
        'no testing experience',
        'only tutorial projects',
        'no production experience (for mid-level+)'
    ],
    experience_expectations={
        'entry': [
            'personal or academic projects',
            'internship experience',
            'foundational programming skills',
            'basic understanding of databases and APIs'
        ],
        'mid': [
            'production system experience',
            'API design and implementation',
            'database optimization',
            'cross-team collaboration',
            'code review participation'
        ],
        'senior': [
            'system architecture decisions',
            'technical leadership',
            'mentoring junior engineers',
            'scalability and performance optimization',
            'cross-functional project leadership'
        ]
    }
)

# Software Engineering - Frontend
SOFTWARE_FRONTEND = FieldConfig(
    name="Software Engineering (Frontend)",
    core_keywords={
        'javascript', 'typescript', 'react', 'vue', 'angular', 'html', 'css',
        'responsive design', 'webpack', 'babel', 'npm', 'yarn',
        'redux', 'state management', 'component design', 'accessibility',
        'performance optimization', 'cross-browser', 'mobile-first'
    },
    supporting_keywords={
        'sass', 'less', 'tailwind', 'styled-components', 'jest', 'cypress',
        'storybook', 'figma', 'design systems', 'seo', 'pwa',
        'graphql', 'rest api', 'websockets', 'animation'
    },
    required_sections=['experience', 'skills', 'projects'],
    impact_metrics=[
        'page load time', 'lighthouse score', 'conversion rate',
        'user engagement', 'accessibility score', 'bundle size',
        'render time', 'user satisfaction'
    ],
    red_flags=[
        'no modern framework experience',
        'no responsive design mention',
        'no accessibility awareness',
        'outdated jQuery-only experience'
    ],
    experience_expectations={
        'entry': [
            'portfolio of projects',
            'modern framework knowledge',
            'responsive design implementation',
            'basic JavaScript proficiency'
        ],
        'mid': [
            'production application development',
            'state management expertise',
            'performance optimization',
            'cross-browser compatibility',
            'component library development'
        ],
        'senior': [
            'architecture decisions',
            'design system creation',
            'technical leadership',
            'performance strategy',
            'mentoring and code quality advocacy'
        ]
    }
)

# Data Science / Machine Learning
DATA_SCIENCE = FieldConfig(
    name="Data Science / Machine Learning",
    core_keywords={
        'python', 'r', 'sql', 'machine learning', 'statistics',
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
        'data analysis', 'data visualization', 'feature engineering',
        'model training', 'model evaluation', 'a/b testing',
        'regression', 'classification', 'clustering', 'nlp', 'computer vision'
    },
    supporting_keywords={
        'jupyter', 'spark', 'hadoop', 'airflow', 'mlflow', 'kubeflow',
        'tableau', 'power bi', 'matplotlib', 'seaborn', 'plotly',
        'aws sagemaker', 'azure ml', 'gcp ai platform',
        'deep learning', 'neural networks', 'xgboost', 'random forest'
    },
    required_sections=['experience', 'skills', 'education', 'projects'],
    impact_metrics=[
        'model accuracy', 'precision', 'recall', 'auc', 'f1 score',
        'revenue impact', 'cost savings', 'efficiency improvement',
        'prediction improvement', 'data volume processed',
        'inference latency', 'model deployment success'
    ],
    red_flags=[
        'no statistical foundation',
        'no production model experience (for mid-level+)',
        'only kaggle competitions',
        'no business impact metrics'
    ],
    experience_expectations={
        'entry': [
            'academic or personal ML projects',
            'statistical analysis experience',
            'data cleaning and preprocessing',
            'basic model training and evaluation'
        ],
        'mid': [
            'production model deployment',
            'end-to-end ML pipeline development',
            'feature engineering expertise',
            'model monitoring and maintenance',
            'cross-functional collaboration'
        ],
        'senior': [
            'ML strategy and architecture',
            'team leadership',
            'business impact focus',
            'research to production pipeline',
            'mentoring data scientists'
        ]
    }
)

# Product Management
PRODUCT_MANAGEMENT = FieldConfig(
    name="Product Management",
    core_keywords={
        'product strategy', 'roadmap', 'prioritization', 'user research',
        'stakeholder management', 'product requirements', 'prd',
        'user stories', 'agile', 'scrum', 'kpis', 'okrs',
        'a/b testing', 'analytics', 'user experience', 'market research',
        'competitive analysis', 'go-to-market', 'product launch'
    },
    supporting_keywords={
        'jira', 'confluence', 'figma', 'sql', 'google analytics',
        'mixpanel', 'amplitude', 'wireframing', 'prototyping',
        'customer interviews', 'usability testing', 'mvp',
        'product-market fit', 'growth', 'retention', 'engagement'
    },
    required_sections=['experience', 'skills'],
    impact_metrics=[
        'user growth', 'dau', 'mau', 'retention rate', 'engagement',
        'conversion rate', 'revenue growth', 'market share',
        'customer satisfaction', 'nps', 'feature adoption',
        'time to market', 'churn reduction'
    ],
    red_flags=[
        'no quantified impact',
        'no cross-functional leadership',
        'no user research experience',
        'purely technical focus (for PM role)'
    ],
    experience_expectations={
        'entry': [
            'product internship or associate role',
            'user research participation',
            'data analysis skills',
            'cross-functional project experience'
        ],
        'mid': [
            'end-to-end product ownership',
            'successful product launches',
            'stakeholder management',
            'data-driven decision making',
            'roadmap development'
        ],
        'senior': [
            'product strategy development',
            'team leadership',
            'business model innovation',
            'market expansion',
            'executive stakeholder management'
        ]
    }
)

# UX/UI Design
UX_UI_DESIGN = FieldConfig(
    name="UX/UI Design",
    core_keywords={
        'user research', 'wireframing', 'prototyping', 'usability testing',
        'user interface', 'user experience', 'interaction design',
        'figma', 'sketch', 'adobe xd', 'invision', 'principle',
        'design systems', 'accessibility', 'responsive design',
        'user flows', 'information architecture', 'visual design',
        'design thinking', 'user-centered design', 'iteration'
    },
    supporting_keywords={
        'html', 'css', 'javascript', 'framer', 'after effects',
        'illustrator', 'photoshop', 'user personas', 'journey mapping',
        'card sorting', 'tree testing', 'heuristic evaluation',
        'a/b testing', 'analytics', 'design sprints'
    },
    required_sections=['experience', 'skills', 'portfolio'],
    impact_metrics=[
        'user satisfaction', 'task completion rate', 'error reduction',
        'time on task', 'conversion improvement', 'engagement increase',
        'accessibility score', 'usability score', 'design system adoption'
    ],
    red_flags=[
        'no portfolio link',
        'no user research experience',
        'only visual design (no UX)',
        'no usability testing mentioned'
    ],
    experience_expectations={
        'entry': [
            'strong portfolio',
            'design tool proficiency',
            'user research participation',
            'basic prototyping skills'
        ],
        'mid': [
            'end-to-end design ownership',
            'user research leadership',
            'design system contribution',
            'cross-functional collaboration',
            'usability testing expertise'
        ],
        'senior': [
            'design strategy',
            'team leadership',
            'design system architecture',
            'stakeholder management',
            'design culture building'
        ]
    }
)

# Marketing
MARKETING = FieldConfig(
    name="Marketing",
    core_keywords={
        'marketing strategy', 'campaign management', 'content marketing',
        'seo', 'sem', 'social media', 'email marketing', 'paid advertising',
        'google analytics', 'google ads', 'facebook ads', 'linkedin ads',
        'marketing automation', 'lead generation', 'conversion optimization',
        'brand management', 'content strategy', 'copywriting',
        'marketing analytics', 'roi', 'cac', 'ltv'
    },
    supporting_keywords={
        'hubspot', 'salesforce', 'mailchimp', 'hootsuite', 'semrush',
        'ahrefs', 'google tag manager', 'wordpress', 'shopify',
        'a/b testing', 'landing pages', 'crm', 'marketing funnel',
        'influencer marketing', 'affiliate marketing', 'pr'
    },
    required_sections=['experience', 'skills'],
    impact_metrics=[
        'revenue growth', 'lead generation', 'conversion rate',
        'roi', 'roas', 'cac', 'ltv', 'engagement rate',
        'traffic growth', 'email open rate', 'click-through rate',
        'brand awareness', 'market share', 'customer acquisition'
    ],
    red_flags=[
        'no quantified results',
        'no digital marketing experience',
        'no analytics skills',
        'vague campaign descriptions'
    ],
    experience_expectations={
        'entry': [
            'campaign execution experience',
            'content creation skills',
            'social media management',
            'basic analytics knowledge'
        ],
        'mid': [
            'campaign strategy and ownership',
            'multi-channel marketing',
            'data-driven optimization',
            'budget management',
            'cross-functional collaboration'
        ],
        'senior': [
            'marketing strategy development',
            'team leadership',
            'brand positioning',
            'market expansion',
            'executive reporting'
        ]
    }
)


# Field registry
FIELD_CONFIGS = {
    'software_backend': SOFTWARE_BACKEND,
    'software_frontend': SOFTWARE_FRONTEND,
    'data_science': DATA_SCIENCE,
    'product_management': PRODUCT_MANAGEMENT,
    'ux_ui_design': UX_UI_DESIGN,
    'marketing': MARKETING
}


def get_field_config(field_key: str) -> FieldConfig:
    """Get configuration for a specific field."""
    return FIELD_CONFIGS.get(field_key, SOFTWARE_BACKEND)


def get_available_fields() -> List[Dict[str, str]]:
    """Get list of available fields for UI selection."""
    return [
        {'key': 'software_backend', 'name': 'Software Engineering (Backend)'},
        {'key': 'software_frontend', 'name': 'Software Engineering (Frontend)'},
        {'key': 'data_science', 'name': 'Data Science / Machine Learning'},
        {'key': 'product_management', 'name': 'Product Management'},
        {'key': 'ux_ui_design', 'name': 'UX/UI Design'},
        {'key': 'marketing', 'name': 'Marketing'}
    ]


def get_experience_level_expectations(field_key: str, level: str) -> List[str]:
    """Get experience expectations for a field and level."""
    config = get_field_config(field_key)
    return config.experience_expectations.get(level, [])
