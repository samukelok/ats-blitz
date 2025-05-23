import sys
import json
import re
import base64
from typing import Dict, List, Tuple
import spacy
import mysql.connector
from collections import defaultdict
from groq import Groq

nlp = spacy.load("en_core_web_sm")

class ResumeAnalyzer:
    def __init__(self):
        # Initialisations
        self._compile_patterns()
        self.job_title_db = self._init_db_connection()
        self.learned_titles = defaultdict(int) 
        
    def _compile_patterns(self):
        """Pre-compiled regex patterns used in analysis"""
        self.section_pattern = re.compile(
            r'^(contact|summary|experience|education|skills|projects)\s*:?$',
            re.I | re.M
        )
        
        self.metric_pattern = re.compile(
            r'(?:\$\d[\d,]+|\d+\s*%|\d+\s*x|\d+\s*\+|\d+\s*years?|\b\d{3,}\b|\d+\s*[\w/]+\b|\d+\+?)',
            re.I
        )
        
        self.quality_patterns = {
            'generic_phrases': re.compile(
                r'team\s*player|hard\s*worker|detail\s*oriented|go\s*getter',
                re.I
            ),
            'pronouns': re.compile(r'\bI\b|\bmy\b|\bme\b'),
            'passive_voice': re.compile(r'\bwas\s+\w+ed\b|\bwere\s+\w+ed\b|\bby\s+the\b', re.I)
        }
        
        self.date_range_pattern = re.compile(
            r'(?:(?:Jan|Feb|Mar|April|May|June|July|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})'
            r'\s*[-–—]\s*'
            r'(?:Present|(?:Jan|Feb|Mar|April|May|June|July|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
            re.I
        )

    def _get_match_strength(self, score: float) -> str:
        """Simple match strength descriptor"""
        if score >= 0.9: return "Excellent"
        if score >= 0.7: return "Good"
        if score >= 0.5: return "Fair"
        return "Weak"

    def analyze_resume(self, resume_text: str, job_title: str) -> Dict:
        try:
            # 1. input validation
            if not resume_text or not isinstance(resume_text, str):
                return self._error_response("Invalid resume text")
            
            if not job_title or not isinstance(job_title, str):
                return self._error_response("Invalid job title")

            # 2. Clean inputs
            clean_text = self._clean_text(resume_text)
            standardized_title = self._standardize_title(job_title)

            # 3. Calculate content score
            content_result = self._analyze_resume_content(clean_text)
            if not isinstance(content_result.get('score'), (int, float)):
                return self._error_response("Invalid content analysis")

            # 4. Calculate title match (0-1 scale)
            title_match = self._calculate_title_match(clean_text, standardized_title)
            if not isinstance(title_match, (int, float)) or not 0 <= title_match <= 1:
                return self._error_response("Invalid title match calculation")

            # 5. Combine scores (70% content, 30% title)
            final_score = (content_result['score'] * 0.7) + (title_match * 100 * 0.3)

            # If title match is less or equal to 0.6, divide the final score by 2 to penelise it
            if title_match <= 0.6:
                final_score /= 2

            self.final_score = final_score

            # 6. Prepare output with debug info
            return {
                'status': 'success',
                'score': min(100, max(0, final_score)),  
                'score_breakdown': {
                    'content_score': content_result['score'],
                    'title_match_score': round(title_match * 100, 1),
                    'title_match_strength': self._get_match_strength(title_match)
                },
                'feedback': content_result.get('feedback', {})
            }

        except Exception as e:
            return self._error_response(f"Analysis error: {str(e)}")

    def _calculate_title_match(self, resume_text: str, job_title: str) -> float:
        """Simplified title matching that searches entire resume"""
        try:
            # Standardize the input title
            standardized_input = self._standardize_title(job_title)
            if not standardized_input:
                return 0.4 
            
            # Search for direct matches
            if standardized_input.lower() in resume_text.lower():
                return 1.0 
            
            # Search for partial matches
            input_words = standardized_input.lower().split()
            resume_lower = resume_text.lower()
            
            # Count how many title words appear in resume
            matches = sum(1 for word in input_words if word in resume_lower)
            match_ratio = matches / len(input_words) if input_words else 0
            
            # Quality thresholds
            if match_ratio >= 0.9: return 1.0    # Nearly all words match
            if match_ratio >= 0.7: return 0.9    # Most words match
            if match_ratio >= 0.5: return 0.7    # Some words match
            
            # Fallback to NLP similarity if no direct matches
            input_doc = nlp(standardized_input.lower())
            resume_doc = nlp(resume_text.lower())
            nlp_similarity = input_doc.similarity(resume_doc)
            
            return max(nlp_similarity, 0.2)  #penelise
        
        except Exception as e:
            print(f"Title matching error: {str(e)}", file=sys.stderr)
            return 0.2  

    def _standardize_title(self, title: str) -> str:
        """Simplified title standardization"""
        if not title or not isinstance(title, str):
            return ""
        
        # Basic cleaning
        title = title.lower().strip()
        title = re.sub(r'[^a-z0-9\s]', '', title)  #
        
        # Common replacements
        replacements = {
            r'\bweb\s*dev\b': 'web developer',
            r'\bsoft(?:ware)?\s*eng(?:ineer)?\b': 'software engineer',
            r'\bdata\s*sci(?:entist)?\b': 'data scientist',
            r'\bfront\s*end\b': 'frontend developer',
            r'\bback\s*end\b': 'backend developer'
        }
        
        for pattern, repl in replacements.items():
            title = re.sub(pattern, repl, title)
        
        return title

    def _learn_job_title(self, title: str):
        """Store new job titles and track frequency"""
        if not self._title_exists(title):
            self.learned_titles[title] += 1
            # Auto-add to DB after seeing title 3 times
            if self.learned_titles[title] >= 3:
                self._add_to_standardized_titles(title)

    def _add_to_standardized_titles(self, title: str):
        """Add new title to database"""
        try:
            cursor = self.job_title_db.cursor()
            query = """INSERT INTO standardised_job_titles 
                      (original_title, standardised_title) 
                      VALUES (%s, %s)"""
            cursor.execute(query, (title, title))
            self.job_title_db.commit()
        except Exception as e:
            print(f"Failed to add title: {e}", file=sys.stderr)

    def _title_exists(self, title: str) -> bool:
        """Check if title exists in database"""
        cursor = self.job_title_db.cursor()
        query = """SELECT 1 FROM standardised_job_titles 
                  WHERE standardised_title = %s LIMIT 1"""
        cursor.execute(query, (title,))
        return cursor.fetchone() is not None
    
    def _init_db_connection(self):
        """Initialize MySQL connection"""
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ats_blitz"
        )
        
    def _find_section_bounds(self, text: str) -> Dict[str, Tuple[int, int]]:
        """Returns {section_name: (start_index, end_index)}"""
        bounds = {}
        matches = list(self.section_pattern.finditer(text))
        
        for i, match in enumerate(matches):
            section = match.group(1).lower()
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(text)
            bounds[section] = (start, end)
        
        return bounds
    
    def _analyze_resume_content(self, clean_text: str) -> Dict:
        """Core analysis of resume content that was previously missing"""
        # Find all sections in the resume
        section_bounds = self._find_section_bounds(clean_text)
        sections = self._detect_sections(clean_text)
        
        # Extract key components
        metrics = self._find_metrics(clean_text)
        action_verbs = [verb for verb in self._load_action_verbs() if verb in clean_text.lower()]
        quality_issues = self._check_quality(clean_text, section_bounds)
        date_ranges = self._find_date_ranges(clean_text)
        
        # Calculate score
        score = self._calculate_score(
            sections=sections,
            metrics=metrics,
            action_verbs=action_verbs,
            text=clean_text,
            quality_issues=quality_issues,
            date_ranges=date_ranges
        )
        
        # Generate feedback
        feedback = self._generate_feedback(
            score=score,
            sections=sections,
            metrics=metrics,
            action_verbs=action_verbs,
            text=clean_text,
            quality_issues=quality_issues,
            date_ranges=date_ranges,
            section_bounds=section_bounds
        )
        
        return {
            'score': score,
            'feedback': feedback
        }

    def _enhance_feedback(self, base_feedback: Dict, title_score: float, standardized_title: str) -> Dict:
        """Enhances feedback with title-specific suggestions"""
        feedback = base_feedback.copy()
        
        # Add title-specific suggestions
        if title_score < 0.3:
            feedback['suggestions'].insert(0, 
                f"CRITICAL: Your resume shows weak alignment with '{standardized_title}' positions")
        elif title_score < 0.6:
            feedback['suggestions'].insert(0,
                f"IMPORTANT: Better align your resume with '{standardized_title}' keywords")
        
        # title score to breakdown
        feedback['score_breakdown']['title_match'] = round(title_score * 100, 1)
        
        return feedback

    def _detect_sections(self, text: str) -> Dict[str, bool]:
        sections = {
            'contact': False,
            'summary': False,
            'experience': False,
            'education': False,
            'skills': False,
            'projects': False
        }
        
        # Check for explicit section headers
        found_headers = set(
            header.lower() for header in 
            self.section_pattern.findall(text)
        )
        
        # Update sections based on found headers
        for section in sections:
            if section in found_headers:
                sections[section] = True
            else:
                # Fallback
                sections[section] = bool(re.search(
                    self._get_section_keywords(section), 
                    text, 
                    re.I
                ))
        
        return sections
    
    def _clean_text(self, text: str) -> str:
        """Cleans and standardizes resume text for analysis"""
        # Remove non-ASCII characters
        text = text.encode('ascii', errors='ignore').decode('ascii')
        
        # Normalise whitespace and line breaks
        text = ' '.join(text.split())
        
        # Remove common resume artifacts
        text = re.sub(r'•|\u2022|\u25E6|\u25AA', ' ', text)  # Bullet points
        text = re.sub(r'\bpage\s*\d+\b', '', text, flags=re.I)  # Page numbers
        text = re.sub(r'http[s]?://\S+', '', text)  # URLs
        
        # Standardise section headers
        text = re.sub(r'\n\s*([A-Z][A-Z\s]+)\s*\n', r'\n\1\n', text)
        
        return text.strip()
    
    def _standardize_title(self, title: str) -> str:
        """Standardises job titles for consistent matching"""
        if not title or not isinstance(title, str):
            return ""
        
        # Convert to lowercase and remove special characters
        title = title.lower().strip()
        title = re.sub(r'[^a-z0-9\s]', '', title)
        
        # Common title normalisations
        replacements = {
            r'\bweb\s*dev\b': 'web developer',
            r'\bsoft(?:ware)?\s*eng(?:ineer)?\b': 'software engineer',
            r'\bdata\s*sci(?:entist)?\b': 'data scientist',
            r'\bux/ui\b': 'ux designer',
            r'\bfull\s*stack\b': 'full stack developer',
            r'\bfront\s*end\b': 'front end developer',
            r'\bback\s*end\b': 'back end developer'
        }
        
        for pattern, replacement in replacements.items():
            title = re.sub(pattern, replacement, title)
        
        # Remove common prefixes/suffixes
        title = re.sub(r'^(senior|junior|lead|principal)\s+', '', title)
        title = re.sub(r'\s+(i|ii|iii|iv|v)$', '', title)
        
        return title.title() 

    def _get_section_keywords(self, section: str) -> str:
        """Returns regex pattern for section content detection"""
        keywords = {
            'contact': r'contact|info|details|email|phone|address|linkedin',
            'summary': r'summary|objective|profile|about me',
            'experience': r'experience|work\s*history|employment',
            'education': r'education|academic|degree|university',
            'skills': r'skills|proficient|competencies|expertise',
            'projects': r'projects|portfolio|case\s*studies'
        }
        return keywords.get(section, '')
    

    def _load_action_verbs(self) -> List[str]:
        """Returns categorized action verbs with strength indicators"""
        return [
        # Leadership & Management  
        'managed', 'led', 'increased', 'reduced', 'achieved', 'developed',  
        'supervised', 'directed', 'coordinated', 'oversaw', 'spearheaded', 'delegated',  
        'organised', 'executed', 'administered', 'facilitated', 'guided', 'chaired',  
        'orchestrated', 'motivated', 'empowered', 'influenced', 'transformed', 'streamlined',  
        
        # Problem-Solving & Analytical  
        'resolved', 'diagnosed', 'investigated', 'analszed', 'evaluated', 'assessed',  
        'identified', 'interpreted', 'synthesised', 'formulated', 'conceptualised', 'devised',  
        'designed', 'troubleshot', 'improved', 'optimised', 'innovated', 'calculated',  
        'forecasted', 'critiqued',  
        
        # Communication & Interpersonal  
        'presented', 'negotiated', 'persuaded', 'advised', 'consulted', 'counseled',  
        'communicated', 'trained', 'educated', 'instructed', 'explained', 'facilitated',  
        'mediated', 'promoted', 'drafted', 'wrote', 'edited', 'proofread', 'published',  
        'corresponded',  
        
        # Technical & IT  
        'developed', 'programmed', 'engineered', 'implemented', 'built', 'designed',  
        'debugged', 'tested', 'automated', 'integrated', 'configured', 'optimised',  
        'maintained', 'updated', 'secured', 'installed', 'networked', 'deployed',  
        'customised', 'coded',  
        
        # Sales & Marketing  
        'sold', 'marketed', 'promoted', 'advertised', 'pitched', 'negotiated',  
        'closed', 'converted', 'generated', 'captured', 'expanded', 'achieved',  
        'maximised', 'upsold', 'strategized', 'launched', 'branded', 'targeted',  
        'forecasted',  
        
        # Finance & Accounting  
        'audited', 'budgeted', 'forecasted', 'analyzed', 'calculated', 'reduced',  
        'allocated', 'balanced', 'estimated', 'reconciled', 'managed', 'reported',  
        'controlled', 'projected', 'processed', 'secured', 'evaluated', 'invested',  
        'costed', 'maximised',  
        
        # Customer Service & Client Relations  
        'assisted', 'supported', 'served', 'resolved', 'advised', 'responded',  
        'addressed', 'improved', 'handled', 'engaged', 'retained', 'upsold',  
        'followed-up', 'welcomed', 'listened', 'recommended', 'satisfied', 'maintained',  
        'advocated', 'collaborated',  
        
        # Teaching & Training  
        'taught', 'instructed', 'educated', 'trained', 'coached', 'mentored',  
        'guided', 'facilitated', 'explained', 'demonstrated', 'designed', 'conducted',  
        'developed', 'adapted', 'assessed', 'evaluated', 'encouraged', 'inspired',  
        'illustrated', 'moderated',  
        
        # Creative & Design  
        'created', 'designed', 'conceptualised', 'illustrated', 'photographed',  
        'sketched', 'drafted', 'produced', 'edited', 'directed', 'styled',  
        'innovated', 'transformed', 'crafted', 'painted', 'filmed', 'animated',  
        'composed', 'curated', 'visualized',  
        
        # Medical & Healthcare  
        'diagnosed', 'treated', 'examined', 'prescribed', 'assisted', 'administered',  
        'monitored', 'evaluated', 'rehabilitated', 'operated', 'conducted', 'educated',  
        'supported', 'coordinated', 'advocated', 'responded', 'recorded', 'managed',  
        'intervened', 'researched',  
        
        # Research & Development  
        'researched', 'investigated', 'analysed', 'examined', 'identified', 'tested',  
        'formulated', 'developed', 'designed', 'evaluated', 'interpreted', 'experimented',  
        'documented', 'validated', 'conceptualised', 'innovated', 'discovered', 'compiled',  
        'compared', 'assessed',  
        
        # Operations & Logistics  
        'coordinated', 'scheduled', 'managed', 'organised', 'optimised', 'facilitated',  
        'streamlined', 'arranged', 'oversaw', 'allocated', 'dispatched', 'supervised',  
        'maintained', 'evaluated', 'implemented', 'standardized', 'delivered',  
        'transported', 'monitored', 'executed',  
        
        # Legal & Compliance  
        'advised', 'negotiated', 'drafted', 'reviewed', 'litigated', 'advocated',  
        'researched', 'analyzed', 'argued', 'assessed', 'interpreted', 'complied',  
        'mediated', 'counseled', 'documented', 'defended', 'filed', 'enforced',  
        'audited', 'arbitrated',  
        
        # Engineering & Manufacturing  
        'engineered', 'designed', 'built', 'manufactured', 'fabricated', 'constructed',  
        'installed', 'assembled', 'tested', 'developed', 'modeled', 'configured',  
        'programmed', 'optimised', 'automated', 'operated', 'improved', 'resolved',  
        'upgraded', 'evaluated',  
        
        # Human Resources  
        'recruited', 'interviewed', 'hired', 'trained', 'assessed', 'managed',  
        'coordinated', 'facilitated', 'developed', 'conducted', 'resolved',  
        'implemented', 'mediated', 'supported', 'negotiated', 'consulted', 'motivated',  
        'retained', 'advised', 'promoted',  
        
        # Environmental & Sustainability  
        'conserved', 'restored', 'monitored', 'evaluated', 'managed', 'implemented',  
        'reduced', 'designed', 'researched', 'developed', 'innovated', 'coordinated',  
        'protected', 'educated', 'audited', 'certified', 'advocated', 'measured',  
        'enhanced', 'enforced'   
        ]

    def _find_metrics(self, text: str) -> List[str]:
        """Enhanced metric extraction with validation"""
        return [
            metric for metric in 
            self.metric_pattern.findall(text)
            if len(metric) > 2  # Filter out small numbers
        ]

    def _check_quality(self, text: str, section_bounds: Dict[str, Tuple[int, int]]) -> Dict[str, bool]:
        """Detects common resume quality issues with section awareness"""
        quality_checks = {
            'generic_phrases': bool(self.quality_patterns['generic_phrases'].search(text)),
            'passive_voice': bool(self.quality_patterns['passive_voice'].search(text)),
            'pronouns': False  # Initialize as False
        }
        
        # Section-aware pronoun check
        allowed_sections = {'summary', 'profile'}
        for section, (start, end) in section_bounds.items():
            if section not in allowed_sections:
                section_text = text[start:end]
                if self.quality_patterns['pronouns'].search(section_text):
                    quality_checks['pronouns'] = True
                    break
        
        return quality_checks

    def _find_date_ranges(self, text: str) -> List[str]:
        """Extracts employment date ranges"""
        return self.date_range_pattern.findall(text)

    def _calculate_score(self, **kwargs) -> int:
        sections = kwargs['sections']
        metrics = kwargs['metrics']
        action_verbs = kwargs['action_verbs']
        text = kwargs['text']
        quality_issues = kwargs['quality_issues']
        date_ranges = kwargs['date_ranges']
        
        # Section scoring (max 40)
        section_score = sum(
            10 if sections[section] else 0
            for section in ['experience', 'education', 'skills']
        ) + sum(
            5 if sections[section] else 0
            for section in ['contact', 'summary', 'projects']
        )
        
        # Metric scoring (max 15)
        metrics_score = min(15, len(metrics) * 2)
        
        # Action verb scoring (max 20)
        verbs_found = sum(1 for verb in action_verbs if verb in text)
        verbs_score = min(20, verbs_found * 2)
        
        # Quality scoring (max 15)
        quality_deductions = sum(
            8 if issue else 0  
            for issue in quality_issues.values()
        )
        quality_score = max(0, 15 - quality_deductions)
        
        # Date range scoring (max 10)
        date_score = 0 if len(date_ranges) < 2 else min(10, len(date_ranges) * 3)
        
        # Combine scores 
        raw_score = (
            section_score + 
            metrics_score + 
            verbs_score + 
            quality_score + 
            date_score
        )
        
        # Normalise to 100 
        return min(100, max(0, raw_score))

    def _generate_feedback(self, **kwargs) -> Dict:
        """Generates comprehensive feedback with prioritized suggestions"""
        score = kwargs['score']
        sections = kwargs['sections']
        metrics = kwargs['metrics']
        action_verbs = kwargs['action_verbs']
        text = kwargs['text']
        quality_issues = kwargs['quality_issues']
        date_ranges = kwargs['date_ranges']
        section_bounds = kwargs.get('section_bounds', {})
        
        feedback = {
            'score_breakdown': {
                'sections': sum(1 for v in sections.values() if v) * 10,
                'metrics': len(metrics) * 2,
                'action_verbs': sum(1 for verb in action_verbs if verb in text) * 2,
                'quality': 15 - sum(5 for issue in quality_issues.values() if issue),
                'dates': len(date_ranges) * 2 
            },
            'missing_sections': [k for k, v in sections.items() if not v],
            'action_verbs_found': sum(1 for verb in action_verbs if verb in text),
            'metrics_found': metrics,
            'quality_issues': quality_issues,
            'date_ranges_found': date_ranges,
            'suggestions': self._generate_suggestions(**kwargs),
            'ai_opinion': self._ai_opinion(text)
        }
        
        return feedback

    def _generate_suggestions(self, **kwargs) -> List[str]:
        """Generates prioritized improvement suggestions"""
        score = kwargs['score']
        sections = kwargs['sections']
        metrics = kwargs['metrics']
        action_verbs = kwargs['action_verbs']
        text = kwargs['text']
        quality_issues = kwargs['quality_issues']
        date_ranges = kwargs['date_ranges']
        section_bounds = kwargs.get('section_bounds', {})
        
        suggestions = []
        
        
        # POSITIVE FEEDBACK REQUIREMENTS
        if (score >= 90 and 
            sections['experience'] and 
            sections['education'] and 
            len(metrics) >= 5 and 
            sum(1 for verb in action_verbs if verb in text) >= 8):
            
            suggestions.append("Outstanding! Your resume exceeds ATS optimization standards.")
        elif score >= 80:
            suggestions.append("Excellent resume! It meets most ATS optimization criteria.")
        elif score >= 75:
            suggestions.append("Great job! Your resume performs well in ATS systems.")
        
        # Section suggestions
        if not sections['experience']:
            suggestions.append("CRITICAL: Add a Work Experience section with position details")
        if not sections['education']:
            suggestions.append("CRITICAL: Include your Education background")
        if not sections['skills']:
            suggestions.append("IMPORTANT: Add a Skills section with relevant competencies")
        
        # Metric suggestions
        if len(metrics) < 3:
            suggestions.append("Boost impact: Add 2-3 quantifiable achievements (e.g., 'Increased sales by 30%')")
        
        # Action verb suggestions
        verbs_found = sum(1 for verb in action_verbs if verb in text)
        if verbs_found < 5:
            suggestions.append("Use more action verbs like 'developed', 'optimised', or 'managed' to describe achievements")
        
        # Quality issue suggestions
        if quality_issues['generic_phrases']:
            suggestions.append("Replace generic phrases like 'team player' with specific examples")
        if quality_issues['pronouns']:
            suggestions.append("Reduce use of pronouns (I/my) in work experience - use action verbs instead")
        if quality_issues['passive_voice']:
            suggestions.append("Convert passive voice to active (e.g., 'was responsible for' → 'managed')")
        
        # Date formatting suggestions
        if len(date_ranges) < 2 and sections['experience']:
            suggestions.append("Include date ranges for all positions (e.g., 'May 2020 - Present')")
        
        return suggestions

    def _error_response(self, error_msg: str) -> Dict:
        """Standardized error format"""
        return {
            'status': 'error',
            'error': error_msg,
            'score': 0,
            'score_breakdown': {
                'content_score': 0,
                'title_match_score': 0,
                'title_match_strength': "N/A"
            },
            'feedback': {
                'suggestions': ["Analysis failed - please check your input"],
                'ai_opinion': self._ai_opinion(error_msg)
            }
        }
    
    # AI Opinion on the resume
    def _ai_opinion(self, resume_text: str) -> str:
        """AI opinion generation"""
        client = Groq(api_key="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")

        # AI Conversation Logic
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume expert who helps users tailor their resumes with precision. Give a detailed opinion on the resume provided (UK English) by taking into consideration the job that the candidate would like to apply for. Remember that the resume is extracted text from a pdf/docx, so ignore the formating and links attached and focus on the core content. ",
                },
                {
                    "role": "user",
                    "content": resume_text + 'job that is being applied for: ' + job_title,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content.strip()


if __name__ == "__main__":
    analyzer = ResumeAnalyzer()
    
    if len(sys.argv) < 3:
        print(json.dumps(analyzer._error_response("Missing arguments")))
        sys.exit(1)
        
    resume_text = base64.b64decode(sys.argv[1]).decode('utf-8')
    job_title = base64.b64decode(sys.argv[2]).decode('utf-8')
    
    result = analyzer.analyze_resume(resume_text, job_title)
    print(json.dumps(result))