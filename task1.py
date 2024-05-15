from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        print("Phone number not found.")

    def find_phone(self, phone):
        return phone if any(p.value == phone for p in self.phones) else None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(dict):
    def add_record(self, record):
        self[record.name.value] = record

    def find(self, name):
        return self.get(name)

    def delete(self, name):
        if name in self:
            del self[name]

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.values():
            if record.birthday and record.birthday.value - today <= timedelta(days=7):
                upcoming_birthdays.append(record)
        return upcoming_birthdays

    def save_to_file(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load_from_file(cls, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return cls()


def parse_input(user_input):
    return user_input.strip().split()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Контакт не знайдено"
        except IndexError:
            return "Вкажіть аргумент для команди"

    return inner

@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Not enough values to add contact. Usage: add <name> <phone>")
    name, phone = args[:2]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message


@input_error
def change_phone(args, book):
    if len(args) < 2:
        raise ValueError("Not enough values to change phone. Usage: change <name> <phone>")
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return "Phone number updated."
    else:
        return "Contact not found."


@input_error
def show_phone(args, book):
    if len(args) < 1:
        raise ValueError("Not enough values to show phone. Usage: phone <name>")
    name = args[0]
    record = book.find(name)
    if record:
        phones = ', '.join(str(p) for p in record.phones)
        return f"Phone number: {phones}" if phones else "No phone numbers found."
    else:
        return "Contact not found."

@input_error
def show_all(book):
    records_info = "\n".join(str(record) for record in book.values())
    return records_info if records_info else "No contacts found."


@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise ValueError("Not enough values to add birthday. Usage: add-birthday <name> <birthday>")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."


@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise ValueError("Not enough values to show birthday. Usage: show-birthday <name>")
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday: {record.birthday}"
        else:
            return "Birthday not set."
    else:
        return "Contact not found."


@input_error
def birthdays(book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join(str(record) for record in upcoming_birthdays)
    else:
        return "No upcoming birthdays."

def main():
    book = AddressBook.load_from_file()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input:  # Додали перевірку на пустий ввід
            print("Please enter a command.")
            continue
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            book.save_to_file()
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
