def get_roadmap(role):
    ROADMAPS = {
        "Data Scientist": [
            "Learn Python & NumPy",
            "Master statistics",
            "Build ML projects",
            "Create a portfolio"
        ],
        "Software Engineer": [
            "Learn DSA",
            "Build projects",
            "Practice system design"
        ],
        "UI/UX Designer": [
            "Learn design principles",
            "Master Figma",
            "Create case studies"
        ],
        "AI Engineer": [
            "Master Python programming",
            "Learn Machine Learning fundamentals (supervised & unsupervised)",
            "Study Deep Learning with TensorFlow/PyTorch",
            "Understand statistics and probability",
            "Build AI projects (NLP, Computer Vision, etc.)",
            "Contribute to open-source AI projects",
            "Create portfolio with real-world AI solutions"
        ],
        "Web Developer": [
            "Learn HTML & CSS fundamentals",
            "Master JavaScript (ES6+)",
            "Learn a frontend framework (React, Vue, or Angular)",
            "Understand backend basics (Node.js or Python)",
            "Learn Git and version control",
            "Build responsive projects",
            "Deploy applications to production"
        ],
        "Business Analyst": [
            "Master SQL for data querying",
            "Excel advanced formulas and pivot tables",
            "Learn data visualization tools",
            "Develop business analysis techniques",
            "Improve communication and presentation skills",
            "Create data-driven insights and reports",
            "Learn industry domain knowledge"
        ]
    }

    return ROADMAPS.get(role, ["Roadmap coming soon"])
