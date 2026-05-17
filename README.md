## CritiqueCounter

CritiqueCounter is a comprehensive Full-Stack Automated Essay Grader, NLP Structural Reviewer, and Analytics Dashboard. It leverages a decoupled architecture via a Django REST Framerwork (DRF) backend and a React (JSX) frontend, providin real-time natural language processing evaluations and an interactive workspace interface.

## System Architecture
* **Backend:** Django, Django REST Framework, SQLite.
* **NLP Pipeline:** Pure Python nlp engine package
wrapping (en_core_web_sm), scikit-learn (vectorization), and textstat (readability heuristics).

 ##  What does it do?
 When you send your essay to this program, it reads through the text very fast and check these things:

 * **Word Count:** It counts how many words you wrote. It checks if you wrote enough to reach your goal.
 * **Sentence Check:** It checks if your sentences are too long. Sentences with too many words are hard to read.
 * **Easy to Read:** It looks at your words and tells you what school grade level can understand your essay.
 * **Joining Words:** It checks if you sued nice joining words (like *however*,*also*)to help your writing flow smoothly

 ## What is done today?

 Web App setup is completed today and alongside with that backend DJANGO(DRF) code is checked and reviewed and NLP engine analyzer code is also reviewed and checked and done today.