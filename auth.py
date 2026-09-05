import json
import logging
from datetime import timedelta
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import jwt as pyjwt
from jwt.exceptions import ImmatureSignatureError
from scalekit import ScalekitClient
from scalekit.common.scalekit import TokenValidationOptions
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Security scheme for Bearer token
security = HTTPBearer()

# Initialize ScaleKit client
scalekit_client = ScalekitClient(
    settings.SCALEKIT_ENVIRONMENT_URL,
    settings.SCALEKIT_CLIENT_ID,
    settings.SCALEKIT_CLIENT_SECRET
)


# Authentication middleware
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/.well-known/") or request.url.path == "/health":
            return await call_next(request)

        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

            token = auth_header.split(" ")[1]

            request_body = await request.body()
            
            # Parse JSON from bytes
            try:
                request_data = json.loads(request_body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                request_data = {}
            
            validation_options = TokenValidationOptions(
              issuer=settings.SCALEKIT_ENVIRONMENT_URL,
              audience=[settings.SCALEKIT_AUDIENCE_NAME],
            )
            
            is_tool_call = request_data.get("method") == "tools/call"
            
            required_scopes = []
            if is_tool_call:
                required_scopes = ["documents:read"] # get required scope for your tool
                validation_options.required_scopes = required_scopes  
            try:
                logger.info(f"Validating token with issuer: {settings.SCALEKIT_ENVIRONMENT_URL}")
                logger.info(f"Validating token with audience: {settings.SCALEKIT_AUDIENCE_NAME}")
                scalekit_client.validate_token(token, options=validation_options)
                logger.info("Token validation successful!")

            except ImmatureSignatureError:
                # Clock skew between local server and ScaleKit — re-validate with 60s leeway
                logger.warning("Clock skew detected (ImmatureSignatureError), re-validating with 60s leeway")
                try:
                    scalekit_client.core_client.get_jwks()
                    kid = pyjwt.get_unverified_header(token)["kid"]
                    key = scalekit_client.core_client.keys[kid]
                    decode_opts = {"verify_iss": True, "verify_aud": True}
                    pyjwt.decode(
                        token,
                        key=key,
                        algorithms=["RS256"],
                        options=decode_opts,
                        issuer=settings.SCALEKIT_ENVIRONMENT_URL,
                        audience=[settings.SCALEKIT_AUDIENCE_NAME],
                        leeway=timedelta(seconds=60),
                    )
                    logger.info("Token validation successful with clock skew tolerance!")
                except Exception as leeway_err:
                    logger.error(f"Token validation failed even with leeway: {leeway_err}")
                    raise HTTPException(status_code=401, detail=f"Token validation failed: {leeway_err}")

            except Exception as e:
                logger.error(f"Token validation error: {str(e)}")
                logger.error(f"Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")

        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": "unauthorized" if e.status_code == 401 else "forbidden", "error_description": e.detail},
                headers={
                    "WWW-Authenticate": f'Bearer realm="OAuth", resource_metadata="{settings.SCALEKIT_RESOURCE_METADATA_URL}"'
                }
            )

        return await call_next(request)