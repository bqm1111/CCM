from typing import List

from pydantic import BaseModel


class A(BaseModel):
    num: int
    name: List[str]
    
a = A(num=1, name=["Minh", "Lan"])
b = A(num=1, name=["Lan", "Minh"])

print(a==b) 
