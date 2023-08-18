# Changelog

## [Unreleased]

### Roadmap

- **Persistence of API Performance Metrics:** Implement a system to persist and analyze API performance over time.
- **Tests:** Add backend tests
- **CI/CD Pipelines:** Establish continuous integration and continuous deployment to streamline development and release
  processes.
- **Training and Deployment of an Open Source LLM:** Investigate and possibly include the training and deployment of an
  open-source Large Language Model within the project scope.
- **CT Pipeline:** It would be hardcore-level cool to implement a continuous training pipeline.
- **Answers correctness:** Add ability to flag an answer as correct or incorrect.
- **Abstract the data access layer:** Make it extensible to work with other databases / DbaS
- **Do you have cool ideas?** Please share them!

## [Version 0.0.1]

### Added

#### Infrastructure Setup

- **Backend:** FastAPI framework used for creating the API.
- **Frontend:** Streamlit application for user interactions.
- **Database:** MongoDB for data persistence.
- **Cloud Providers:** DO integration for hosting and related services.

#### Q&A Persistence Implementation

- Added persistence for questions and answers, enabling historical tracking, analytics and hopefully data to fine-tune
  the thing.

#### Authentication System

- Auth system to avoid bots and human trolls.

---

This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format, and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
