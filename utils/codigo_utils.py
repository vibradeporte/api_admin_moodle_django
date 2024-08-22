import hashlib

def hash_code(code: str) -> str:
    """
    ## **Descripción:**
        Genera el hash SHA-256 del código ingresado y lo devuelve como una cadena hexadecimal.
    
    ## **Parámetros obligatorios:**
        code (str): El código a cifrar (como un string).
    
    ## **Retorna:**
        El código cifrado en formato hexadecimal.
    """
    hashed_code = hashlib.sha256(code.encode()).hexdigest()
    return hashed_code

def verify_code_hash(input_code: str, stored_hashed_code: str) -> bool:
    """
    ## **Descripción:**
        Verifica si el código ingresado, una vez cifrado, coincide con el hash almacenado.
    
    ## **Parámetros obligatorios:**
        input_code (str): El código ingresado por el usuario (como un string).
        stored_hashed_code (str): El hash del código almacenado en la base de datos.
    
    ## **Retorna:**
        True si el código ingresado coincide con el código almacenado, False en caso contrario.
    """
    hashed_input_code = hashlib.sha256(input_code.encode()).hexdigest()
    return hashed_input_code == stored_hashed_code