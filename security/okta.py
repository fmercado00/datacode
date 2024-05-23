from fastapi import HTTPException, status
from jose import jwt, JWTError
import httpx
from pydantic import BaseModel


OKTA_AUDIENCE ="api://default"

class TokenData(BaseModel):
    iss: str
    aud: str

class OktaJWTValidator:
    def __init__(self, issuer: str):
        self.issuer = issuer
        self.jwks_uri = f"{issuer}/.well-known/openid-configuration"

    def get_signing_keys(self):
        with httpx.Client() as client:
            oidc_config = client.get(self.jwks_uri).json()
            jwks_uri = oidc_config['jwks_uri']
            return client.get(jwks_uri).json()

    def validate_token(self, token: str):
        try:
            unverified_header = jwt.get_unverified_header(token)
            jwks = self.get_signing_keys()
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            if rsa_key:
                payload = jwt.decode(
                    token, rsa_key, algorithms=["RS256"],
                    audience=OKTA_AUDIENCE,
                    issuer=self.issuer
                )
                return payload
            else:
                raise JWTError("Appropriate key not found.")
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )

