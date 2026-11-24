from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.dependencies import get_current_user
from auth.dependencies import get_current_user
from database import get_db
from model import Activity, Realm, User
from schemes.realm import RealmOut, RealmSelect
from schemes.user import UserOut

router = APIRouter(prefix="/realms", tags=["Realms"])


@router.get("", response_model=list[RealmOut])
def list_realms(db: Session = Depends(get_db)):
    return db.query(Realm).order_by(Realm.id).all()


@router.post("/select", response_model=UserOut)
def select_realm(
    data: RealmSelect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    realm = db.query(Realm).filter(Realm.id == data.realm_id).first()
    if not realm:
        raise HTTPException(status_code=404, detail="Realm not found")

    current_user.current_realm_id = realm.id
    db.add(Activity(
        user_id=current_user.id,
        type="realm_selected",
        message=f"{current_user.full_name} entered the {realm.name} realm!",
    ))
    db.commit()
    db.refresh(current_user)
    return current_user