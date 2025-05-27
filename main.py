from src.utils import check_exist_data
from src.analyzer import Vacancy, VacancyAnalyzer
from src.storage import JSONSaver
from src.config import DATA_DIR, DEFAULT_TOP_N, MAX_TOP_N


def user_interaction():
    """Функция интерфейса с пользователем. В ней проводится опрос и по результату ответа выполняются получение данных
    с сайта hh.ru, фильтрация полученных данных, вывод в консоль и сохранение результатов фильтрации данных"""
    try:
        # 1. Получение данных
        search_query = input("Введите запрос (например, 'Python'): ").strip()
        if not search_query:
            raise ValueError("Поисковый запрос не может быть пустым")

        hh_data = check_exist_data(search_query)
        vacancies = Vacancy.cast_to_object_list(hh_data, search_query)

        # 2. Фильтрация по ключевому слову
        keyword = input("Введите ключевое слово в описании (Enter - пропустить): ").strip()
        if keyword:
            vacancies = VacancyAnalyzer(vacancies).filter_by_keyword(keyword)

        # 3. Фильтрация по стажу с поддержкой дробных значений
        experience = input(
            "Стаж: введите значение \"От\" (Число. Иное - пропустить): ").replace(" ", "").replace(",", ".")
        if experience:
            vacancies = VacancyAnalyzer(vacancies).filter_by_experience(experience)

        # 4. Фильтрация по зарплате
        salary_input = input(
            "Введите диапазон зарплат (например, '100000-150000', Enter - пропустить): ").replace(" ", "")
        if salary_input:
            vacancies = VacancyAnalyzer(vacancies).filter_by_salary(salary_input)

        # 5. Сортировка и топ-N
        input_top_n = input(
            f"Введите Топ-N вакансий по зарплате (число, Enter - вывести {DEFAULT_TOP_N} вакансий): ").replace(" ", "")
        vacancies_sorted = VacancyAnalyzer(vacancies).get_top_n(input_top_n)

        # 6. Вывод результата
        print(f"\nНайдено Топ-{len(vacancies_sorted)} вакансий по зарплате для '{search_query}':")
        for p in vacancies_sorted:
            print(p)

        # 7. Сохранение результатов отбора и сортировки
        saver = JSONSaver(search_query)
        for vacancy in vacancies_sorted:
            saver.add_vacancy(vacancy)
        print(f"\nДанные сохранены {DATA_DIR} в {search_query}_processed.json")

    except ValueError as err:
        print(f"Ошибка ввода: {err}")


if __name__ == "__main__":
    while True:
        user_interaction()
        if input("\nБудет новый запрос? (y/n): ").lower() not in ['y', 'н']:
            break
