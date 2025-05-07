import os
from datetime import UTC, datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from utils.logger import LoggerConfig
# from logger import LoggerConfig

logger = LoggerConfig("jwt_utils", debug=True).get_logger()

load_dotenv()

class TokenJwt:
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY no está configurada.")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Token expira en 5 minutos
        
        self.FERNET_KEY = os.getenv("FERNET_KEY")
        if not self.FERNET_KEY:
            raise ValueError("FERNET_KEY no está configurada.")
        self.cipher_suite = Fernet(self.FERNET_KEY)

    def create_access_token(self, user_data: dict):
        """Genera token JWT cifrado para usuarios de tu aplicación"""
        try:
            logger.info("Generando token de acceso")
            to_encode = user_data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            logger.debug(f"expire:{expire}- now: {datetime.now(timezone.utc)}-- now+:{datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)}")
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
            encrypted_token = self.cipher_suite.encrypt(encoded_jwt.encode())
            return encrypted_token.decode()
        except Exception as e:
            logger.error(f"Error al generar token: {e}")
            return None

    def validate_token(self, token: str):
        """Valida el token y devuelve payload o error"""
        try:
            logger.info("Validando token de acceso")
            decrypted_token = self.cipher_suite.decrypt(token.encode()).decode()
            payload = jwt.decode(decrypted_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
            # Verificar expiración
            expire = payload.get("exp")
            if expire is None:
                return None, "Token sin fecha de expiración"
                
            # Convertir el timestamp a datetime UTC y comparar
            expire_datetime = datetime.fromtimestamp(expire, tz=timezone.utc)
            now_datetime = datetime.now(timezone.utc)
            
            logger.debug(f"expire: {expire_datetime}, now: {now_datetime}")
            
            if expire_datetime < now_datetime:
                logger.debug("Token expirado")
                return None, "Token expirado"
            logger.debug(f"payload: {payload}")
            return payload, None
        except JWTError as e:
            logger.error(f"Error al validar token: {e}")
            return None, "Token inválido"
        

if __name__ == "__main__":
    token = "gAAAAABoEDO_5OvwPBvVJhVw1W2dnd-rBhMSHWt986PESQXhvDNQSGDEOPjL8vLJ80VRht0B2_4kEHNy25Uy6h_t1mOZ4OHPgXwcZH2eT9z5gjEbGouayLFOC0a_0GjfNLT--lOvZ6dnSUQE49n6-GTWUk7JA98UoRxxVSa19Y8Y1o_Vn9CPFvegTMUw-x0jkNTnUA_XrKIllgDJnr2jT9GURjS74k6GUAWz0-Z2-RzQRvy8_QLGEwbpaRnISV0xtjMIi4rvU5IfdKREMM0Am-YfIoyPUHTE-dFacGdyD1jGLBqPZlApQEY= "
    data, message = TokenJwt().validate_token(token)
    print(f"data: {data}, {message}")