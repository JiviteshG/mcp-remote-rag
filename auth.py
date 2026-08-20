import json
import logging
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from scalekit import ScalekitClient
from scalekit.common.scalekit import TokenValidationOptions
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings