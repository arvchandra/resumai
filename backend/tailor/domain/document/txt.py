from .base import Document


class TxtDocument(Document):
    def parse_file_text(self, file):
        with open(file, 'rb') as f:
            print(f.read())

    def generate_copy(self):
        pass


!f() { git stash && git checkout master && git pull && git checkout - && git merge master && git stash pop; }; f