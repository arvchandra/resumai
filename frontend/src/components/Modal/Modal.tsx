import React from "react";
import { createPortal } from "react-dom";

import "./Modal.css";

interface ModalProps {
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  children: React.ReactNode;
  dialogRef: React.Ref<HTMLDialogElement>;
};

const Modal = ({ confirmText = "OK", cancelText = "Cancel", onConfirm, onCancel, children, dialogRef }: ModalProps) => {
  const modalRoot = document.getElementById('modal-root');
  if (!modalRoot) return null;
  
  return createPortal(
    <dialog ref={dialogRef} className="modal">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
      <div className="btn-action-row">
        <button className="btn btn-small btn-cancel" onClick={onCancel}>{cancelText}</button>
        {confirmText && 
          <button className="btn btn-small btn-primary" onClick={onConfirm}>
            {confirmText}
          </button>
        }
      </div>
    </dialog>,
    modalRoot
  )
}

export default Modal;
