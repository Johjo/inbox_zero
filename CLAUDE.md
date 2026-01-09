Lors des commits, on applique conventionnal commit

Dans l'ordre : 
- les tests doivent passer
- mypy doit indiquer que tout est OK

Lorsque tu crées un use case, je veux que tu utilises le pattern Port et Adapter.
Pour les tests de use case, tu dois utiliser une implémentation ForTest.

Pour l'injection de dépendance, tu vas utiliser pyqure :

## Injection de dépendances avec pyqure

**Initialisation :**
```python
from pyqure import Key, pyqure, PyqureMemory

memory: PyqureMemory = {}
(provide, inject) = pyqure(memory)
```

**Enregistrement de dépendances :**
```python
provide(Key("email_reader", EmailReader), email_reader_instance)
provide(Key("smtp_port", int), 3025)
```

**Injection de dépendances :**
```python
reader = inject(Key("email_reader", EmailReader))
port = inject(Key("smtp_port", int))
```

**Règles importantes :**
- Utilise toujours `Key("nom", Type)` pour type safety
- Les types doivent correspondre exactement (ou être des sous-types)
- `KeyError` si la clé n'existe pas
- `TypeError` si le type ne correspond pas
- Tu peux partager la même `memory` entre plusieurs instances pyqure
- Tu peux override une clé en appelant `provide` plusieurs fois

**Dans les tests :**
```python
@pytest.fixture
def dependencies():
    memory: PyqureMemory = {}
    (provide, inject) = pyqure(memory)
    # Enregistrer les dépendances pour les tests
    provide(Key("repo", UserRepository), UserRepositoryForTest())
    return inject

def test_use_case(dependencies):
    repo = dependencies(Key("repo", UserRepository))
    use_case = CreateUserUseCase(repo)
    # ...
```
