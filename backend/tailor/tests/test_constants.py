EXPECTED_COLUMNS = {
    "test_arvind_resume.pdf": 1,
    "test_max_resume.pdf": 2
}

BULLETS_TO_REDACT = {
    "test_arvind_resume.pdf": [
        'Pursued freelance projects in music production and video editing, expanding creative and technical versatility.',
        'Developed the Django/Python/React/Typescript/Postgres Learning Management Platform and the Django Admin.',
        'Led a technical debt resolution strategy in collaboration with the CTO, which resulted in consistent allotment of time and resources to fixing bugs and improving user experience.',
        'Deployed the Docker application to AWS through a customized GitHub Actions pipeline, which included linting, unit and integration testing, and feature-flag testing on both Staging and Production servers.', # Causing problems with next job experience spacing
        'Generated 300% increase in revenue for the Press Release product by converting a basic HTML form into a more robust and user-friendly single-page React application.',
        'Developed React/Typescript components and a Django REST Framework API, which enabled features such as bulk purchases, discount codes, and Stripe payments, incorporating both server-side and client-side validation.',
        'Reduced average debugging time by 50% by enabling breakpoint-debugging of code running inside Docker containers, in both Visual Studio Code and PyCharm.',
        'Developed the Django/Python/MySQL online news websites and the Django Admin using Django/Jinja templates, HTML, CSS, and Javascript/jQuery.',
        'Led the implementation of Agile/Scrum development, including sprints, retroactives, and JIRA tickets/epics.',
        'Generated $10,000 in weekly ad sales revenue by implementing an HTML5/CSS video ad on our landing page.',
        'Developed a Django REST Framework API that delivered cached results to the frontend Used Cars search website.',
        'Achieved 500% improvement in time efficiency (5 days to 2 hours) for our team of writers by creating an automated scraping framework that retrieved car deals from numerous vehicle manufacturer websites.',
        'Interviewed and hired senior Django developers.',
        'Established a robust testing framework by writing over 300 unit tests.',
        'Lowered annual costs by $15,000 by reassessing IBM Cognos Reports usage and reducing license purchases.',
        'Received a letter of commendation from the client for outstanding performance in understanding the business requirements, delivering high-quality and secure application features, and meeting critical government deadlines.',
    ],
    "test_max_resume.pdf": [
        "Refactored legacy Whatsapp API and expanded internal tooling in Ruby to surface errors, reducing support request volume by 15%.",
        "Engineered data ingestion pipeline API across microservices using Python and PostgreSQL for B2C loan product, reducing admin maintenance by 80%.",
        "Ideated event timeline internal tool using asynchronous Python, REST APIs and PostgreSQL to reduce support requests by 25%.",
    ]
}

BULLETS_ABOVE_FIRST_REDACTED = {
    "test_arvind_resume.pdf": "Designed and developed a full-stack Django/React application integrating AI-driven prompts and third-party APIs.",
    "test_max_resume.pdf": "Deputy engineer for async AWS FIFO queue migration in Ruby to address timestamp-sensitive concurrency problem for Service-Level-Agreement(SLA) feature used by enterprise customers; leading post-release handover."
}

BULLETS_BELOW_FIRST_REDACTED = {
    "test_arvind_resume.pdf": "Traveled to India to take care of my parents and oversee the construction of our new house.",
    "test_max_resume.pdf": "Led development of RESTful API to fetch real-time message delivery status of Whatsapp outbound marketing campaigns."
}

TEXT_BELOW_CONSECUTIVE_REDACTED = {
    "test_arvind_resume.pdf": "The Motley Fool",
    "test_max_resume.pdf": "CENTER FOR LONG-TERM CYBERSECURITY | Graduate Researcher"
}

CONSECUTIVE_REDACTED_INDEX = {
    "test_arvind_resume.pdf": 5,
    "test_max_resume.pdf": 1
}

TEXT_BELOW_LAST_REDACTED = {
    "test_arvind_resume.pdf": "University of Michigan - Ann Arbor, MI",
    "test_max_resume.pdf": "TD INTERNATIONAL"
}