# 파이썬은 선택적으로 타입 힌트(type hint)를 지원합니다.

def get_full_name(first_name, last_name):
    full_name = first_name.title() + " " + last_name.title()
    # title() 메서드는 문자열의 각 단어의 첫 글자를 대문자로 변환합니다.
    return full_name
print(get_full_name("john", "doe"))  # John Doe

# 타입 추가하기
# first_name : str, last_name : str

def get_full_name(first_name : str, last_name : str):
    full_name = first_name.title() + " " + last_name.title()
    return full_name
print(get_full_name("john", "doe"))  # John Doe

def get_name_with_age(name: str, age: int):
    name_with_age = name + " is this old: " + str(age)
    return name_with_age

# Simple 타입: int, str, float, bool, bytes

def get_items(item_a: str, item_b: int, item_c: float, item_d:bool, item_e:bytes):
    return item_a, item_b, item_c, item_d, item_e


# 타입 매개변수를 활용한 Generic(제네릭) 타입
# dict, list, set, tuple과 같은 값을 저장할 수 있는 데이터 구조가 있고, 내부의 값은 각자의 타입을 가질 수 있다.
# 타입과 내부 타입을 선언하기 위해서는 파이썬 표준 모듈인 typing을 사용해야 한다.
from typing import List
# 3.9 이전 버전에서는 typing.List 사용

def process_items_list(items: list[str]): # 대괄호 안의 내부 타입은 "타입 매개변수(type parameter)"라고 부른다.
    for item in items:
        print(item)

def process_item_tuple(items: tuple[int, int, str]):
    return items

process_tuple = process_item_tuple((3, 4, "hello"))
print(process_tuple)

def process_item_set(items: set[bytes]):
    return items

items = process_item_set("hello")
print(items)

def process_item_dict(prices: dict[str, float]):
    for item_name, item_price in prices.items():
        print(item_name)
        print(item_price)

# 변수 prices는 dict 타입이며, 키는 str 타입, 값은 float 타입을 가진다.

process_item_dict({"apple":0.5})

# Optional 타입
# 값이 None일 수도 있는 경우에 사용
from typing import Optional

def say_hi(name: Optional[str] = None):
    if name is not None:
        return f"Hi {name}"
    else:
        return "Hello world"

print(say_hi("Alice"))
print(say_hi())

class Person:
    def __init__(self, name:str):
        self.name = name

def get_person_name(one_person: Person):
    return one_person.name

person = Person("Bob")
print(get_person_name(person))  # Bob


# Pydantic 모델
# Pydantic은 데이터 검증(Validation)을 위한 파이썬 라이브러리입니다.


from datetime import datetime

from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str = "John Doe"
    signup_ts: datetime | None = None
    friends: list[int] = []

external_data = {
    "id": "123",
    "signup_ts": "2023-10-01 12:22",
    "friends": [1, "2", b"3"],
}

user = User(**external_data)
print(user)
print(user.id) # 123