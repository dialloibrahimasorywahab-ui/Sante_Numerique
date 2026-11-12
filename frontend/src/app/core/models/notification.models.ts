export type TypeNotification =
  | 'LIT_URGENCE'
  | 'PATIENT_ARRIVE'
  | 'NOUVEAU_RDV'
  | 'HOSPITALISATION'
  | 'ALERTE_CLINIQUE'
  | 'RAPPEL_RDV'
  | 'PRISE_MEDICAMENT'
  | 'INFO';

export type DestinataireRole =
  | 'TOUS'
  | 'ADMINISTRATEUR'
  | 'MEDECIN'
  | 'INFIRMIER'
  | 'PATIENT';

export interface NotificationHospitaliereDto {
  id_notification: number;
  idNotification: number;
  type_notification: TypeNotification;
  typeNotification: TypeNotification;
  type_display?: string;
  titre: string;
  message: string;
  donnees?: Record<string, any>;
  destinataire_role: DestinataireRole;
  destinataireRole: DestinataireRole;
  destinataire_user?: number | null;
  lu: boolean;
  date_creation: string;
  dateCreation: string;
  actif: boolean;
}

export interface LiveAlertToast {
  id: string;
  type: TypeNotification;
  titre: string;
  message: string;
  timestamp: Date;
  donnees?: Record<string, any>;
}
