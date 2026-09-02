export interface ServiceHospitalier {
  id_service: number;
  idService?: number;
  nom_service: string;
  nomService?: string;
  nom_service_display?: string;
  nomServiceDisplay?: string;
  description?: string | null;
  bureau_localisation?: string | null;
  bureauLocalisation?: string | null;
  actif: boolean;
  icon?: string;
  displayNom?: string;
  displayDesc?: string;
  badgeCountMedecins?: number;
}
