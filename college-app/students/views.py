import json
import logging

from bson import ObjectId
from bson.errors import InvalidId
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from .db import get_database, get_students_collection

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """The request body is not a valid student."""


def _object_id(value):
    """Spring Data stored ids as ObjectId; fall back to the raw string otherwise."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return value


def _serialize(doc):
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name", ""),
        "age": doc.get("age"),
        "city": doc.get("city", ""),
    }


def _error(message, status):
    return JsonResponse({"error": message}, status=status)


def _read_student(request):
    try:
        data = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        raise ValidationError("Request body must be valid JSON.")
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")

    name = data.get("name")
    city = data.get("city")
    age = data.get("age")

    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
        raise ValidationError("name is required (up to 100 characters).")
    if not isinstance(city, str) or not city.strip() or len(city.strip()) > 100:
        raise ValidationError("city is required (up to 100 characters).")
    if isinstance(age, bool) or not isinstance(age, int) or not 1 <= age <= 120:
        raise ValidationError("age must be a whole number between 1 and 120.")

    return {"name": name.strip(), "age": age, "city": city.strip()}


@csrf_exempt
@require_http_methods(["GET", "POST"])
def student_list(request):
    """GET /students lists all students. POST /students adds one."""
    try:
        students = get_students_collection()
        if request.method == "GET":
            docs = students.find().sort("_id", 1)
            return JsonResponse([_serialize(doc) for doc in docs], safe=False)

        payload = _read_student(request)
        students.insert_one(payload)  # adds "_id" to payload
        return JsonResponse(_serialize(payload), status=201)
    except ValidationError as exc:
        return _error(str(exc), 400)
    except PyMongoError:
        logger.exception("MongoDB error in student_list")
        return _error("Database is unavailable.", 503)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def student_detail(request, student_id):
    """GET, PUT or DELETE /students/<id>."""
    try:
        students = get_students_collection()
        key = {"_id": _object_id(student_id)}

        if request.method == "GET":
            doc = students.find_one(key)
        elif request.method == "PUT":
            doc = students.find_one_and_update(
                key,
                {"$set": _read_student(request)},
                return_document=ReturnDocument.AFTER,
            )
        else:
            if students.delete_one(key).deleted_count == 0:
                return _error("Student not found.", 404)
            return HttpResponse(status=204)

        if doc is None:
            return _error("Student not found.", 404)
        return JsonResponse(_serialize(doc))
    except ValidationError as exc:
        return _error(str(exc), 400)
    except PyMongoError:
        logger.exception("MongoDB error in student_detail")
        return _error("Database is unavailable.", 503)


@require_GET
def health(request):
    """Liveness: the process is up. Does not touch MongoDB."""
    return JsonResponse({"status": "UP"})


@require_GET
def ready(request):
    """Readiness: MongoDB answers a ping."""
    try:
        get_database().command("ping")
    except PyMongoError:
        return JsonResponse({"status": "DOWN"}, status=503)
    return JsonResponse({"status": "UP"})
