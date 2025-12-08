testset = [
    {
        "inputs": {"question": "Which decision-making techniques are included in the 'Decision Analysis' module?"},
        "expectations": {"expected_response": "Techniques include classical MCDA methods like AHP, ELECTRE, and PROMETHEE, as well as non-additive approaches such as fuzzy integrals."},
    },
    {
        "inputs": {"question": "When is the 2A internship memory due?"},
        "expectations": {"expected_response": "The internship memory must be submitted before September 30th."},
    },
    {
        "inputs": {"question": "What is studied in structural and environmental optimization?"},
        "expectations": {"expected_response": "Life Cycle Assessment (LCA) applied to building design, material comparisons, and scenario evaluation to minimize environmental impact."},
    },
    {
        "inputs": {"question": "What is studied in soil-structure interaction?"},
        "expectations": {"expected_response": "Design of shallow and deep foundations, soil pressure calculations, and water impact on foundations according to Eurocodes."},
    },
    {
        "inputs": {"question": "What is studied in management of built heritage and rehabilitation?"},
        "expectations": {
            "expected_response": "Evaluation of existing buildings, envelope rehabilitation, energy performance, structural conception, execution methods and interaction between soil and structure."
        }
    },
    {
        "inputs": {"question": "What is the purpose of the final PFE report?"},
        "expectations": {"expected_response": "The final report presents the completed work, methodology, results, and reflections on the project, while respecting confidentiality rules."},
    },
    {
        "inputs": {"question": "How do I pay my rent at la Meuh?"},
        "expectations": {"expected_response": "Choosing direct debit is simple and recommended: direct debits are made after the 20th of the current month. You also have the option of paying by credit card, check payable to MdE, or in cash. The monthly aid is deducted directly from the rent. For this type of payment, the rent must be paid in advance."},
    },
    {
        "inputs": {"question": "What is underpinning?"
        },
        "expectations": {
            "expected_response": "A set of techniques that strengthen and stabilize foundations by transferring loads to deeper soil layers."
        }
    },
    {
        "inputs": {"question": "What is a mur manteau?"},
        "expectations": {
            "expected_response": "An external insulation system used to rehabilitate the building envelope and improve energy performance."
        }
    },
    {
        "inputs": {"question": "What is an Enterprise Operating System (EOS)?"},
        "expectations": {
            "expected_response": "An EOS is a conceptual framework behaving like a computer operating system but applied to enterprises to monitor, orchestrate, and control operations based on enterprise models."
        }
    },
    {
        "inputs": {"question": "What is studied in Terrassement?"},
        "expectations": {
            "expected_response": "Methods and techniques for earthworks, optimizing soil balance, machinery characteristics, work scheduling, special structures and cost studies."
        }
    },
    {
        "inputs": {"question": "What are the prerequisites for Terrassement?"},
        "expectations": {
            "expected_response": "General mechanics, MMC, soil mechanics, rock mechanics and geology."
        }
    },
    {
        "inputs": {"question": "What topics are included in the Reinforcement Learning section?"},
        "expectations": {"expected_response": "The Reinforcement Learning section introduces reward-based learning, Markov decision processes, value-based methods such as Q-learning, policy gradient approaches, and practical applications of RL algorithms."},
    },
    {
        "inputs": {"question": "Is it allowed to use AI as a learning assistant?"},
        "expectations": {"expected_response": "Yes. AI may support learning by explaining concepts and generating examples, but cannot replace the student's own work."},
    },
    {
        "inputs": {"question": "Are additional documents required for internships abroad?"},
        "expectations": {"expected_response": "Yes. Students must provide social security affiliation certificates, European insurance cards, repatriation insurance, and other documents depending on the destination country."},
    },
    {
        "inputs": {"question": "Do I need French social insurance for the university?"},
        "expectations": {"expected_response": "Yes, French social insurance is mandatory in France. You will be instructed in the beginning of your study during the first week, with the help of the administrative staff."},
    },
    {
        "inputs": {"question": "What topics are covered in the Deep Learning section of the module?"},
        "expectations": {"expected_response": "The Deep Learning section covers neural network fundamentals, backpropagation, convolutional neural networks, recurrent neural networks, optimization techniques, regularization, and applied machine learning pipelines."},
    },
    {
        "inputs": {"question": "How to obtain official documents at la Meuh (accommodation certificate, rent receipt, etc.)?"},
        "expectations": {"expected_response": "We provide, upon request by email, an accommodation certificate, a rent receipt after payment, and CAF certificates to be completed."},
    },
    {
        "inputs": {"question": "What is the objective of the Advanced Mathematics for Machine Learning course?"},
        "expectations": {"expected_response": "The course explains mathematical and optimisation tools underlying machine learning techniques such as linear regression, SVMs, neural networks, and sparse learning."},
    },
    {
        "inputs": {"question": "What is the time commitment for the 'Decision Analysis' course?"},
        "expectations": {"expected_response": "The module involves 50 teaching hours, split evenly between the 'Uncertainty Theories' and 'Multiple Criteria Decision Analysis' courses, along with independent study and project work."},
    },
    {
        "inputs": {"question": "Can you explain the format of the 'Decision Analysis' module?"},
        "expectations": {"expected_response": "This module is divided into two courses: 'Uncertainty Theories' and 'Multiple Criteria Decision Analysis.' Each course includes lectures, hands-on labs, seminars, and evaluations."},
    },
    {
        "inputs": {"question": "What is the purpose of using phase diagrams in metallurgy?"},
        "expectations": {"expected_response": "Phase diagrams help predict equilibrium phases, understand transformations, and determine the microstructures achievable through thermal treatments."},
    },
    {
        "inputs": {"question": "What are the learning outcomes of the Heuristic Optimisation class?"},
        "expectations": {"expected_response": "Students learn to develop realistic optimisation methods and assess solution quality and computational efficiency."},
    },
    {
        "inputs": {"question": "What is the main objective of the UE I2ER_8_1 Environnement, Energie, Risques?"},
        "expectations": {"expected_response": "Its goal is to introduce students to ecosystems resilience, energy resource needs, and risk analysis, preparing them for specialization in Semesters 8–10."},
    },
    {
        "inputs": {"question": "Which teaching modules are included in the UE I2ER_8_1?"},
        "expectations": {"expected_response": "Risques industriels et naturels, Ecosystèmes et biodiversité, Enjeux énergétiques et systèmes électriques, and Étude d'impact."},
    },
    {
        "inputs": {"question": "What is air quality management?"},
        "expectations": {
            "expected_response": "Air quality management refers to the strategies and techniques used to monitor, assess, and improve the quality of the air to protect human health and the environment."
        }
    },
    {
        "inputs": {"question": "What are the main sources of air pollution?"},
        "expectations": {
            "expected_response": "Typical air pollution sources include industrial emissions, vehicle exhaust, domestic heating, agriculture, and natural sources like wildfires or dust storms."
        }
    },
    {
        "inputs": {"question": "What is particulate matter (PM)?"},
        "expectations": {
            "expected_response": "Particulate matter (PM) refers to tiny solid or liquid particles suspended in the air, such as PM10 and PM2.5, which can penetrate the respiratory system."
        }
    },
    {
        "inputs": {"question": "What does PM2.5 mean?"},
        "expectations": {
            "expected_response": "PM2.5 refers to particles with a diameter of 2.5 micrometers or smaller, known to pose significant health risks due to their ability to reach deep into the lungs."
        }
    },
    {
        "inputs": {"question": "What are the health impacts of air pollution?"},
        "expectations": {
            "expected_response": "Air pollution can cause respiratory diseases, cardiovascular issues, reduced lung function, allergies, and long-term conditions such as asthma or COPD."
        }
    },
    {
        "inputs": {"question": "What skills am I expected to have before entering the 2IA program at IMT Mines Alès?"},
        "expectations": {
            "expected_response": "You should be comfortable with basic programming, mathematics and problem solving. Each pedagogical guide specifies any additional prerequisites for its module."
        }
    },
    {
        "inputs": {"question": "Are all modules in the 2IA curriculum taught in English?"},
        "expectations": {
            "expected_response": "Not all modules are taught in English. Some are delivered entirely in French, while others may provide English materials. The language depends on the teaching team."
        }
    },
    {
        "inputs": {"question": "How difficult is the advanced machine learning module compared to earlier ML courses?"},
        "expectations": {
            "expected_response": "It is more demanding, requiring strong foundations in mathematics, probability, programming and basic machine learning concepts."
        }
    }
]