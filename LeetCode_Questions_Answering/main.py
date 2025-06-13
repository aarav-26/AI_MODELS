import os
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_theories(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        theories = re.split(r'-{10,}', content)
    return theories

def extract_question_title(theory_text):
    match = re.search(r'QUESTION \d+: (.+)', theory_text)
    if match:
        return match.group(1)
    return None

def slugify(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return text.replace(' ', '-')

def get_answer_file(slug, answers_dir):
    files = os.listdir(answers_dir)
    for file in files:
        if file.startswith(slug):
            with open(os.path.join(answers_dir, file), 'r') as f:
                return f.read()
    return "Answer file not found."

def find_matches(user_input, theories, texts):
    vectorizer = TfidfVectorizer().fit(texts + [user_input])
    vectors = vectorizer.transform(texts + [user_input])
    similarity = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    matches = []
    for idx, score in enumerate(similarity):
        if score >= 0.1:
            matches.append((texts[idx], theories[idx], score))
    matches.sort(key=lambda x: x[2], reverse=True)
    return matches

def main_menu():
    print("\n🎛️ MAIN MENU:")
    print("1️⃣  Title-based Search")
    print("2️⃣  Theory-based Search")
    print("0️⃣  Exit")

def main():
    theories = load_theories('theory.txt')
    titles = [extract_question_title(theory) or "" for theory in theories]

    while True:
        main_menu()
        choice = input("\nSelect an option: ").strip()

        if choice == '0':
            print("👋 Exiting. Happy coding!")
            break

        if choice not in ['1', '2']:
            print("❌ Invalid choice. Try again.")
            continue

        while True:
            query = input("\nEnter your query text (or type 'menu' to return to Main Menu): ").strip()
            if query.lower() == 'menu':
                break

            if choice == '1':
                matches = find_matches(query, theories, titles)
            else:
                matches = find_matches(query, theories, theories)

            if not matches:
                print("\n❌ No match found. Try a different or clearer query.")
                continue

            for idx, (text, theory, score) in enumerate(matches):
                title = extract_question_title(theory)
                if not title:
                    continue

                print(f"\n📖 Matched Title: {title} (Score: {score:.3f})")
                print(f"\n{theory}\n")

                fetch_ans = input(f"Do you want to fetch the answer code for '{title}'? (yes/no/menu): ").strip().lower()
                if fetch_ans == 'menu':
                    break
                if fetch_ans == 'yes':
                    slug = slugify(title)
                    answer = get_answer_file(slug, 'answers')
                    print(f"\n💻 Answer Code for '{title}':\n{answer}\n")
                    print("=" * 100)
                    break  # show one match only if accepted

                if idx == len(matches) - 1:
                    print("\n❌ No more matches available.")

            else:
                # executed only if loop didn’t break → i.e. reached end without 'menu'
                continue
            break  # breaks if user typed 'menu'

if __name__ == '__main__':
    main()
