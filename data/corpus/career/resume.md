% ===============================================================
% Pryce Tharpe – One-Page Résumé (Compact with Aligned Dates)
% ===============================================================

\documentclass[letterpaper,10pt]{article}

% ---------- Packages ----------
\usepackage[margin=0.6in]{geometry}
\usepackage{parskip}
\setlength{\parskip}{5pt} % Reduced from 6pt
\usepackage{enumitem}
\setlist[itemize]{itemsep=3pt,topsep=4pt,parsep=0pt,leftmargin=*} % Slightly more breathing room in bullets
\usepackage[T1]{fontenc}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}
\titleformat{\section}{\large\bfseries}{}{0.4em}{}[\titlerule]
\titlespacing*{\section}{0pt}{5pt}{5pt} % Reduced from 6pt
\usepackage{array}
\renewcommand{\arraystretch}{1.15} % Slightly taller line spacing in tables
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\begin{document}
\thispagestyle{empty}

% ===== Header =====
\begin{tabular*}{\textwidth}{@{}l@{\extracolsep{\fill}}r@{}}
  {\huge\bfseries Pryce Tharpe} & (317)~519~5098 — \href{mailto:tharpep\_pro@outlook.com}{\nolinkurl{tharpep\_pro@outlook.com}} \\
  & \href{https://pryce-tharpe.dev}{pryce-tharpe.dev} — \href{https://linkedin.com/in/pryce-tharpe}{linkedin.com/in/pryce-tharpe} — \href{https://github.com/tharpep}{github.com/tharpep} \\
\end{tabular*}
\vspace{4pt}\hrule\vspace{5pt}

% ===== Professional Experience =====
\section*{Professional Experience}
\textbf{Mesh Systems}, Carmel, IN \hfill \textit{May 2025 -- Present}\\
\textit{Software Engineer Intern}\\
Rotated through Cloud, Mobile \& DevOps teams on AI enablement, automation, and feature development.

\vspace{5pt}
\textbf{AI System Prompt \& Internal Enablement Platform} \hfill \textit{Jun -- Aug 2025}
\begin{itemize}
  \item Developed a master IDE prompt that standardized AI-assisted coding workflows across the company.
  \item Built internal GPT-based tools and facilitated 17 short enablement sessions (AI 101/workshops) for 20+ engineers across multiple teams, standardizing AI usage across the org.
\end{itemize}

\textbf{Azure DevOps Sprint Scorecard Extension} \hfill \textit{Jun -- Aug 2025}
\begin{itemize}
  \item Designed and delivered an Azure DevOps extension with real-time sprint dashboards for project tracking.
  \item Converted a static HTML prototype into a production-ready React/Next.js solution, integrating backend data from a junior intern's service.
\end{itemize}

\textbf{Financial Report Automation} \hfill \textit{May -- Jun 2025}
\begin{itemize}
  \item Designed and launched an automated ETL pipeline with Microsoft Fabric and SQL, cutting monthly Azure reporting from 3 hours to under 10 minutes.
\end{itemize}

% ===== Academic & Personal Projects =====
\section*{Academic \& Personal Projects}
\textbf{ECE461 Software Engineering} --- Package Registry System \hfill \textit{Aug -- Dec 2025}
\begin{itemize}[itemsep=2pt,topsep=2pt]
  \item Designed complete AWS deployment infrastructure (ECS/Fargate, ECR, S3, CloudWatch) with zero-downtime CI/CD pipeline using GitHub Actions and OIDC authentication.
  \item Implemented LLM-based evaluation metrics using Purdue GenAI Studio API for performance claims and reproducibility assessment.
\end{itemize}

\textbf{Senior Design} --- Smart Glasses GenAI Subsystem \hfill \textit{Aug -- Dec 2025}
\begin{itemize}[itemsep=2pt,topsep=2pt]
  \item Built complete GenAI microservice with RAG system and multi-provider LLM abstraction; integrated across web, mobile, and embedded subsystems.
\end{itemize}

\textbf{MY-AI} --- Personal AI Assistant Framework \hfill \textit{Oct 2025 -- Present}
\begin{itemize}[itemsep=2pt,topsep=2pt]
  \item Developing modular AI framework with RAG implementation and LLM provider abstraction; includes Docker containerization and pytest test suite.
\end{itemize}

% ===== Additional Experience =====
\section*{Additional Experience}
\textbf{Purdue Rack and Roll}, West Lafayette, IN \hfill \textit{Aug 2023 -- Aug 2025}\\
Managed daily operations and customer experience in a high-responsibility, two-person setting.

\textbf{Royal Pin Woodland}, Indianapolis, IN \hfill \textit{Aug 2021 -- Aug 2024}\\
Trained 5+ new hires, led 2--4-person teams, and supervised a 70-lane center during peak hours.

% ===== Education =====
\section*{Education}
\textbf{Purdue University}, West Lafayette, IN \hfill \textit{Aug 2022 -- May 2026}\\
Bachelor of Science in Computer Engineering\\
\textit{Current Coursework}: Software Engineering, Machine Learning, Software Senior Design

% ===== Skills =====
\section*{Skills}
\textbf{Technical}: Python, C/C++, React, Next.js, TypeScript, AWS (ECS, ECR, S3, CloudWatch, IAM), Docker, CI/CD (GitHub Actions), Azure DevOps, Microsoft Fabric, SQL, FastAPI, RAG Systems, LLM Integration, Prompt Engineering, Git/GitHub, pytest

\end{document}