import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1024")
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    url = Path("web_mock/index.html").resolve().as_uri()
    driver.get(url)
    yield driver
    driver.quit()

@pytest.fixture(autouse=True)
def reload_page(driver):
    url = Path("web_mock/index.html").resolve().as_uri()
    driver.get(url)

class TestRegistrationFormUI:
    """Автоматизированные UI тесты для страницы регистрации"""

    def fill_form(self, driver, login="valid_user", password="Password123!", confirm="Password123!",
                  gender="male", email="user@mail.ru", day="15", month="5", year="1995"):
        if login is not None:
            el = driver.find_element(By.ID, "login")
            el.clear()
            el.send_keys(login)
        if password is not None:
            el = driver.find_element(By.ID, "password")
            el.clear()
            el.send_keys(password)
        if confirm is not None:
            el = driver.find_element(By.ID, "confirmPassword")
            el.clear()
            el.send_keys(confirm)
        if gender is not None:
            sel = Select(driver.find_element(By.ID, "gender"))
            sel.select_by_value(gender)
        if email is not None:
            el = driver.find_element(By.ID, "email")
            el.clear()
            el.send_keys(email)
        if day is not None:
            el = driver.find_element(By.ID, "birthDay")
            el.clear()
            el.send_keys(day)
        if month is not None:
            sel = Select(driver.find_element(By.ID, "birthMonth"))
            sel.select_by_value(month)
        if year is not None:
            el = driver.find_element(By.ID, "birthYear")
            el.clear()
            el.send_keys(year)

    def test_tc01_successful_registration_button_becomes_green(self, driver):
        submit_btn = driver.find_element(By.ID, "submitBtn")
        assert not submit_btn.is_enabled()
        # Initial color is gray (#B0B0B0)
        assert "active" not in submit_btn.get_attribute("class")

        self.fill_form(driver)
        # Trigger blur to ensure event updates
        driver.find_element(By.ID, "birthYear").send_keys("\t")

        assert submit_btn.is_enabled()
        assert "active" in submit_btn.get_attribute("class")
        submit_btn.click()
        success = driver.find_element(By.ID, "successMsg")
        assert "visible" in success.get_attribute("class")

    def test_tc02_login_min_length_validation(self, driver):
        login_input = driver.find_element(By.ID, "login")
        login_input.send_keys("abcd")  # 4 chars < 5
        driver.find_element(By.ID, "password").click()  # blur login
        err = driver.find_element(By.ID, "err-login")
        assert "visible" in err.get_attribute("class")
        assert "Минимум 5" in err.text

    def test_tc03_login_max_length_validation(self, driver):
        login_input = driver.find_element(By.ID, "login")
        login_input.send_keys("a" * 21)  # 21 chars > 20
        driver.find_element(By.ID, "password").click()
        err = driver.find_element(By.ID, "err-login")
        assert "visible" in err.get_attribute("class")
        assert "Максимум 20" in err.text

    def test_tc04_login_allowed_chars_cyrillic_and_symbols(self, driver):
        login_input = driver.find_element(By.ID, "login")
        login_input.send_keys("Иван_Тест-@")
        driver.find_element(By.ID, "password").click()
        err = driver.find_element(By.ID, "err-login")
        assert "visible" not in err.get_attribute("class")

    def test_tc05_login_invalid_special_chars(self, driver):
        login_input = driver.find_element(By.ID, "login")
        login_input.send_keys("user#test!")  # # and ! not allowed in login
        driver.find_element(By.ID, "password").click()
        err = driver.find_element(By.ID, "err-login")
        assert "visible" in err.get_attribute("class")

    def test_tc06_password_min_length(self, driver):
        pwd_input = driver.find_element(By.ID, "password")
        pwd_input.send_keys("12345")  # 5 < 6
        driver.find_element(By.ID, "login").click()
        err = driver.find_element(By.ID, "err-password")
        assert "visible" in err.get_attribute("class")
        assert "Минимум 6" in err.text

    def test_tc07_password_max_length(self, driver):
        pwd_input = driver.find_element(By.ID, "password")
        pwd_input.send_keys("a" * 34)  # 34 > 33
        driver.find_element(By.ID, "login").click()
        err = driver.find_element(By.ID, "err-password")
        assert "visible" in err.get_attribute("class")
        assert "Максимум 33" in err.text

    def test_tc08_confirm_password_mismatch(self, driver):
        pwd_input = driver.find_element(By.ID, "password")
        pwd_input.send_keys("Secret123!")
        confirm_input = driver.find_element(By.ID, "confirmPassword")
        confirm_input.send_keys("Different123!")
        driver.find_element(By.ID, "login").click()
        err = driver.find_element(By.ID, "err-confirmPassword")
        assert "visible" in err.get_attribute("class")
        assert "Пароли не совпадают" in err.text

    def test_tc09_gender_selection_male_and_female(self, driver):
        gender_sel = Select(driver.find_element(By.ID, "gender"))
        options = [o.text for o in gender_sel.options if o.text]
        assert "Мужской" in options
        assert "Женский" in options
        assert len(options) == 2

    def test_tc10_email_allowed_domains(self, driver):
        valid_emails = ["test@mail.ru", "user@gmail.com", "admin@yandex.ru"]
        email_input = driver.find_element(By.ID, "email")
        err = driver.find_element(By.ID, "err-email")

        for email in valid_emails:
            email_input.clear()
            email_input.send_keys(email)
            driver.find_element(By.ID, "login").click()
            assert "visible" not in err.get_attribute("class"), f"Email {email} should be valid"

    def test_tc11_email_disallowed_domain(self, driver):
        email_input = driver.find_element(By.ID, "email")
        email_input.send_keys("test@yahoo.com")
        driver.find_element(By.ID, "login").click()
        err = driver.find_element(By.ID, "err-email")
        assert "visible" in err.get_attribute("class")

    def test_tc12_day_bounds_and_numeric(self, driver):
        day_input = driver.find_element(By.ID, "birthDay")
        err = driver.find_element(By.ID, "err-birthDay")

        # Non-numeric
        day_input.send_keys("ab")
        driver.find_element(By.ID, "login").click()
        assert "visible" in err.get_attribute("class")

        # Out of range 32
        day_input.clear()
        day_input.send_keys("32")
        driver.find_element(By.ID, "login").click()
        assert "visible" in err.get_attribute("class")

        # Valid day 15
        day_input.clear()
        day_input.send_keys("15")
        driver.find_element(By.ID, "login").click()
        assert "visible" not in err.get_attribute("class")

    def test_tc13_month_dropdown_contains_12_months(self, driver):
        month_sel = Select(driver.find_element(By.ID, "birthMonth"))
        valid_months = [o.text for o in month_sel.options if o.text]
        assert len(valid_months) == 12

    def test_tc14_year_max_age_90_years(self, driver):
        year_input = driver.find_element(By.ID, "birthYear")
        err = driver.find_element(By.ID, "err-birthYear")

        # More than 90 years ago (e.g. 1920)
        year_input.send_keys("1920")
        driver.find_element(By.ID, "login").click()
        assert "visible" in err.get_attribute("class")
        assert "Максимальный возраст 90 лет" in err.text

        # Valid year 2000
        year_input.clear()
        year_input.send_keys("2000")
        driver.find_element(By.ID, "login").click()
        assert "visible" not in err.get_attribute("class")

    def test_tc15_active_field_highlight_dark_blue_and_label_lifted(self, driver):
        login_input = driver.find_element(By.ID, "login")
        box = driver.find_element(By.ID, "box-login")
        label = driver.find_element(By.ID, "label-login")

        login_input.click()
        assert "active" in box.get_attribute("class")
        assert "lifted" in label.get_attribute("class")

    def test_tc16_mandatory_fields_have_asterisks(self, driver):
        mandatory_box_ids = ["box-login", "box-password", "box-confirmPassword", "box-email", "box-birthDay", "box-birthMonth", "box-birthYear"]
        for b_id in mandatory_box_ids:
            box = driver.find_element(By.ID, b_id)
            asterisk = box.find_element(By.CLASS_NAME, "asterisk")
            assert asterisk.text == "*"
