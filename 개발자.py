class Developer:
    def __init__(self, name, language, experience):
        self.name = name
        self.language = language
        self.experience = experience

    def introduce(self):
        print(
            f"안녕하세요. 저는 {self.name}이며 "
            f"{self.language} 개발 경력 {self.experience}년입니다."
        )

    def code(self):
        print(f"{self.language}로 개발 작업을 수행합니다.")