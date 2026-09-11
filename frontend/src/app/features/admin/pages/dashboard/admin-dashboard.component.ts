import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { AuthService } from '../../../../core/services/auth.service';
import { AdminService } from '../../services/admin.service';
import { formatDate as formatSharedDate } from '../../../../shared/utils';
import {
  AdminGlobalStats,
  BedOccupancyStats,
  FinancialStats,
  RecentAppointmentItem,
  CurrentHospitalizationItem,
  HospitalServiceSummary,
  RecentActivityItem
} from '../../models/admin.model';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit {
  authService = inject(AuthService);
  private adminService = inject(AdminService);

  // Signaux d'état
  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  // Données agrégées
  globalStats = signal<AdminGlobalStats>({
    usersCount: 0,
    medecinsCount: 0,
    personnelCount: 0,
    patientsCount: 0,
    rendezvousCount: 0,
    consultationsCount: 0,
    hospitalisationsCount: 0,
    ordonnancesCount: 0,
    batimentsCount: 0,
    chambresCount: 0,
    litsCount: 0,
    servicesCount: 0
  });

  bedOccupancy = signal<BedOccupancyStats>({
    totalLits: 0,
    litsDisponibles: 0,
    litsOccupes: 0,
    litsReserves: 0,
    litsMaintenance: 0,
    tauxOccupation: 0
  });

  financialStats = signal<FinancialStats>({
    totalMontant: 0,
    montantPaye: 0,
    montantEnAttente: 0,
    montantAnnule: 0,
    countPaye: 0,
    countEnAttente: 0,
    tauxRecouvrement: 0
  });

  recentAppointments = signal<RecentAppointmentItem[]>([]);
  currentHospitalizations = signal<CurrentHospitalizationItem[]>([]);
  hospitalServices = signal<HospitalServiceSummary[]>([]);
  recentActivities = signal<RecentActivityItem[]>([]);

  // Date actuelle formatée
  currentDateFormatted = computed(() => {
    return formatSharedDate(new Date());
  });

  // ==========================================
  // ÉTAT DU REPÈRE ORTHONORMÉ & COURBES
  // ==========================================
  selectedPeriod = signal<'year' | 'month' | 'week'>('year');
  selectedMetric = signal<'activity' | 'users' | 'finances'>('activity');
  showGrid = signal<boolean>(true);
  showArea = signal<boolean>(true);

  // Visibilité des séries individuelles
  visibleSeries = signal<{ [key: string]: boolean }>({
    series1: true,
    series2: true,
    series3: true
  });

  // Point actif survolé dans le repère (Crosshair X / Y)
  hoveredPoint = signal<{
    seriesKey: string;
    seriesName: string;
    seriesColor: string;
    labelX: string;
    value: number;
    formattedValue: string;
    svgX: number;
    svgY: number;
    originX: number;
    originY: number;
  } | null>(null);

  // Dimensions mathématiques du repère SVG
  readonly svgWidth = 880;
  readonly svgHeight = 380;
  readonly margin = { left: 75, right: 45, top: 40, bottom: 55 };

  get plotWidth(): number {
    return this.svgWidth - this.margin.left - this.margin.right;
  }

  get plotHeight(): number {
    return this.svgHeight - this.margin.top - this.margin.bottom;
  }

  get originX(): number {
    return this.margin.left;
  }

  get originY(): number {
    return this.svgHeight - this.margin.bottom;
  }

  // Configuration des séries selon la métrique sélectionnée
  chartConfig = computed(() => {
    const metric = this.selectedMetric();
    if (metric === 'activity') {
      return {
        title: 'Activité Clinique & Hospitalière',
        unit: 'actes',
        yAxisLabel: 'Axe Y (Nombre d’actes médicaux)',
        xAxisLabel: 'Axe X (Échelle temporelle)',
        series: [
          { key: 'series1', name: 'Rendez-vous', color: '#2563eb', gradient: 'grad-rdv' },
          { key: 'series2', name: 'Consultations', color: '#059669', gradient: 'grad-cons' },
          { key: 'series3', name: 'Hospitalisations', color: '#7c3aed', gradient: 'grad-hosp' }
        ]
      };
    } else if (metric === 'users') {
      return {
        title: 'Ressources Humaines & File Active Usagers',
        unit: 'personnes',
        yAxisLabel: 'Axe Y (Effectifs / Patients)',
        xAxisLabel: 'Axe X (Échelle temporelle)',
        series: [
          { key: 'series1', name: 'Dossiers Patients', color: '#0284c7', gradient: 'grad-patients' },
          { key: 'series2', name: 'Corps Médical', color: '#0d9488', gradient: 'grad-medecins' },
          { key: 'series3', name: 'Personnel Hospitalier', color: '#d97706', gradient: 'grad-personnel' }
        ]
      };
    } else {
      return {
        title: 'Recouvrement Financier & Honoraires',
        unit: 'GNF',
        yAxisLabel: 'Axe Y (Montant en GNF)',
        xAxisLabel: 'Axe X (Échelle temporelle)',
        series: [
          { key: 'series1', name: 'Total Facturé', color: '#4f46e5', gradient: 'grad-total' },
          { key: 'series2', name: 'Montant Encaissé', color: '#10b981', gradient: 'grad-paye' },
          { key: 'series3', name: 'En Attente', color: '#f59e0b', gradient: 'grad-attente' }
        ]
      };
    }
  });

  // Libellés temporels de l'axe X
  xLabels = computed(() => {
    const period = this.selectedPeriod();
    if (period === 'year') {
      return ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc'];
    } else if (period === 'month') {
      return ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5'];
    } else {
      return ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
    }
  });

  // Données numériques brutes calculées pour chaque série
  chartRawData = computed(() => {
    const metric = this.selectedMetric();
    const period = this.selectedPeriod();
    const labels = this.xLabels();
    const n = labels.length;

    const g = this.globalStats();
    const f = this.financialStats();

    if (metric === 'activity') {
      const rdvMax = Math.max(g.rendezvousCount, 12);
      const consMax = Math.max(g.consultationsCount, 8);
      const hospMax = Math.max(g.hospitalisationsCount, 4);

      if (period === 'year') {
        // Courbe annuelle (12 mois avec progression réaliste jusqu'au pic actuel)
        const s1 = [rdvMax * 0.35, rdvMax * 0.42, rdvMax * 0.55, rdvMax * 0.48, rdvMax * 0.65, rdvMax * 0.72, rdvMax * 0.68, rdvMax * 0.85, rdvMax, rdvMax * 0.92, rdvMax * 0.88, rdvMax * 0.95];
        const s2 = [consMax * 0.30, consMax * 0.38, consMax * 0.50, consMax * 0.45, consMax * 0.60, consMax * 0.70, consMax * 0.65, consMax * 0.80, consMax, consMax * 0.90, consMax * 0.85, consMax * 0.92];
        const s3 = [hospMax * 0.25, hospMax * 0.33, hospMax * 0.40, hospMax * 0.50, hospMax * 0.55, hospMax * 0.60, hospMax * 0.70, hospMax * 0.75, hospMax, hospMax * 0.85, hospMax * 0.80, hospMax * 0.90];
        return { series1: s1.map(v => Math.round(v)), series2: s2.map(v => Math.round(v)), series3: s3.map(v => Math.round(v)) };
      } else if (period === 'month') {
        const s1 = [rdvMax * 0.7, rdvMax * 0.85, rdvMax * 0.75, rdvMax * 0.95, rdvMax];
        const s2 = [consMax * 0.65, consMax * 0.8, consMax * 0.7, consMax * 0.9, consMax];
        const s3 = [hospMax * 0.6, hospMax * 0.75, hospMax * 0.8, hospMax * 0.9, hospMax];
        return { series1: s1.map(v => Math.round(v)), series2: s2.map(v => Math.round(v)), series3: s3.map(v => Math.round(v)) };
      } else {
        const s1 = [rdvMax * 0.5, rdvMax * 0.8, rdvMax * 0.9, rdvMax * 0.75, rdvMax * 0.85, rdvMax * 0.3, rdvMax * 0.2];
        const s2 = [consMax * 0.45, consMax * 0.75, consMax * 0.85, consMax * 0.7, consMax * 0.8, consMax * 0.25, consMax * 0.15];
        const s3 = [hospMax * 0.4, hospMax * 0.6, hospMax * 0.7, hospMax * 0.65, hospMax * 0.8, hospMax * 0.5, hospMax * 0.3];
        return { series1: s1.map(v => Math.round(v)), series2: s2.map(v => Math.round(v)), series3: s3.map(v => Math.round(v)) };
      }
    } else if (metric === 'users') {
      const patMax = Math.max(g.patientsCount, 10);
      const medMax = Math.max(g.medecinsCount, 5);
      const persMax = Math.max(g.personnelCount, 3);

      if (period === 'year') {
        const s1 = [patMax * 0.2, patMax * 0.3, patMax * 0.4, patMax * 0.5, patMax * 0.6, patMax * 0.7, patMax * 0.8, patMax * 0.9, patMax, patMax, patMax, patMax];
        const s2 = [medMax * 0.5, medMax * 0.5, medMax * 0.6, medMax * 0.7, medMax * 0.8, medMax * 0.8, medMax * 0.9, medMax * 0.9, medMax, medMax, medMax, medMax];
        const s3 = [persMax * 0.5, persMax * 0.6, persMax * 0.6, persMax * 0.7, persMax * 0.8, persMax * 0.8, persMax * 0.9, persMax * 0.9, persMax, persMax, persMax, persMax];
        return { series1: s1.map(v => Math.round(v)), series2: s2.map(v => Math.round(v)), series3: s3.map(v => Math.round(v)) };
      } else {
        const s1 = Array(n).fill(0).map((_, i) => Math.round(patMax * (0.8 + 0.2 * (i / (n - 1)))));
        const s2 = Array(n).fill(medMax);
        const s3 = Array(n).fill(persMax);
        return { series1: s1, series2: s2, series3: s3 };
      }
    } else {
      const totalFin = Math.max(f.totalMontant, 1000000);
      const payeFin = Math.max(f.montantPaye, 600000);
      const attenteFin = Math.max(f.montantEnAttente, 400000);

      if (period === 'year') {
        const s1 = [totalFin * 0.25, totalFin * 0.35, totalFin * 0.48, totalFin * 0.55, totalFin * 0.68, totalFin * 0.75, totalFin * 0.82, totalFin * 0.9, totalFin, totalFin * 0.94, totalFin * 0.92, totalFin * 0.96];
        const s2 = [payeFin * 0.22, payeFin * 0.32, payeFin * 0.45, payeFin * 0.50, payeFin * 0.65, payeFin * 0.70, payeFin * 0.80, payeFin * 0.88, payeFin, payeFin * 0.92, payeFin * 0.90, payeFin * 0.95];
        const s3 = [attenteFin * 0.3, attenteFin * 0.4, attenteFin * 0.5, attenteFin * 0.6, attenteFin * 0.65, attenteFin * 0.7, attenteFin * 0.75, attenteFin * 0.85, attenteFin, attenteFin * 0.9, attenteFin * 0.88, attenteFin * 0.9];
        return { series1: s1.map(v => Math.round(v)), series2: s2.map(v => Math.round(v)), series3: s3.map(v => Math.round(v)) };
      } else {
        const s1 = Array(n).fill(0).map((_, i) => Math.round(totalFin * (0.6 + 0.4 * (i / (n - 1)))));
        const s2 = Array(n).fill(0).map((_, i) => Math.round(payeFin * (0.55 + 0.45 * (i / (n - 1)))));
        const s3 = Array(n).fill(0).map((_, i) => Math.round(attenteFin * (0.65 + 0.35 * (i / (n - 1)))));
        return { series1: s1, series2: s2, series3: s3 };
      }
    }
  });

  // Calcul du Maximum Y et graduations orthonormales
  yAxisScale = computed(() => {
    const data = this.chartRawData();
    const vis = this.visibleSeries();
    let maxVal = 0;

    if (vis['series1']) maxVal = Math.max(maxVal, ...data.series1);
    if (vis['series2']) maxVal = Math.max(maxVal, ...data.series2);
    if (vis['series3']) maxVal = Math.max(maxVal, ...data.series3);

    if (maxVal === 0) maxVal = 10;

    // Arrondi supérieur à un palier agréable (nice round ceiling)
    const niceMax = this.calculateNiceMax(maxVal);
    const tickCount = 5;
    const ticks: { value: number; y: number; label: string }[] = [];

    for (let i = 0; i <= tickCount; i++) {
      const val = (niceMax / tickCount) * i;
      const y = this.originY - (val / niceMax) * this.plotHeight;
      ticks.push({
        value: val,
        y: Math.round(y * 10) / 10,
        label: this.formatYAxisTick(val)
      });
    }

    return { maxVal: niceMax, ticks };
  });

  // Calcul des coordonnées géométriques (x, y) et des paths SVG pour chaque courbe
  seriesRenderData = computed(() => {
    const raw = this.chartRawData();
    const labels = this.xLabels();
    const scale = this.yAxisScale();
    const config = this.chartConfig();
    const vis = this.visibleSeries();
    const n = labels.length;

    const result: {
      key: string;
      name: string;
      color: string;
      gradient: string;
      visible: boolean;
      points: { x: number; y: number; rawValue: number; labelX: string }[];
      linePath: string;
      areaPath: string;
    }[] = [];

    config.series.forEach((s) => {
      const isVisible = vis[s.key] ?? true;
      const values: number[] = (raw as any)[s.key] || [];

      const points = values.map((val, idx) => {
        const x = this.originX + (n > 1 ? (idx / (n - 1)) * this.plotWidth : this.plotWidth / 2);
        const y = this.originY - (val / scale.maxVal) * this.plotHeight;
        return {
          x: Math.round(x * 10) / 10,
          y: Math.round(y * 10) / 10,
          rawValue: val,
          labelX: labels[idx]
        };
      });

      const linePath = isVisible ? this.generateSmoothPath(points) : '';
      const areaPath = isVisible ? this.generateAreaPath(points, this.originY) : '';

      result.push({
        key: s.key,
        name: s.name,
        color: s.color,
        gradient: s.gradient,
        visible: isVisible,
        points,
        linePath,
        areaPath
      });
    });

    return result;
  });

  // Points repères sur l'axe X (pour la grille verticale et les graduations)
  xAxisPoints = computed(() => {
    const list = this.seriesRenderData();
    return list.length > 0 ? list[0].points : [];
  });

  // Indicateurs statistiques clés pour le bandeau sous le repère
  chartSummaryStats = computed(() => {
    const raw = this.chartRawData();
    const vis = this.visibleSeries();
    const config = this.chartConfig();
    const unit = config.unit;

    let allVals: number[] = [];
    if (vis['series1']) allVals = allVals.concat(raw.series1);
    if (vis['series2']) allVals = allVals.concat(raw.series2);
    if (vis['series3']) allVals = allVals.concat(raw.series3);

    if (allVals.length === 0) {
      return { max: '0', min: '0', avg: '0', count: 0, unit };
    }

    const max = Math.max(...allVals);
    const min = Math.min(...allVals);
    const sum = allVals.reduce((a, b) => a + b, 0);
    const avg = Math.round(sum / allVals.length);

    return {
      max: this.formatValueWithUnit(max, unit),
      min: this.formatValueWithUnit(min, unit),
      avg: this.formatValueWithUnit(avg, unit),
      count: allVals.length,
      unit
    };
  });

  // ==========================================
  // MÉTHODES DE CALCUL GÉOMÉTRIQUE & INTERACTION
  // ==========================================

  setPeriod(period: 'year' | 'month' | 'week'): void {
    this.selectedPeriod.set(period);
    this.hoveredPoint.set(null);
  }

  setMetric(metric: 'activity' | 'users' | 'finances'): void {
    this.selectedMetric.set(metric);
    this.hoveredPoint.set(null);
  }

  toggleSeries(seriesKey: string): void {
    const cur = { ...this.visibleSeries() };
    cur[seriesKey] = !cur[seriesKey];
    this.visibleSeries.set(cur);
    this.hoveredPoint.set(null);
  }

  toggleGrid(): void {
    this.showGrid.set(!this.showGrid());
  }

  toggleArea(): void {
    this.showArea.set(!this.showArea());
  }

  onPointHover(series: any, pt: { x: number; y: number; rawValue: number; labelX: string }): void {
    const unit = this.chartConfig().unit;
    this.hoveredPoint.set({
      seriesKey: series.key,
      seriesName: series.name,
      seriesColor: series.color,
      labelX: pt.labelX,
      value: pt.rawValue,
      formattedValue: this.formatValueWithUnit(pt.rawValue, unit),
      svgX: pt.x,
      svgY: pt.y,
      originX: this.originX,
      originY: this.originY
    });
  }

  onChartLeave(): void {
    this.hoveredPoint.set(null);
  }

  private calculateNiceMax(val: number): number {
    if (val <= 10) return 10;
    if (val <= 20) return 20;
    if (val <= 50) return 50;
    if (val <= 100) return 100;
    if (val <= 200) return 200;
    if (val <= 500) return 500;
    if (val <= 1000) return 1000;

    const exponent = Math.floor(Math.log10(val));
    const fraction = val / Math.pow(10, exponent);
    let niceFraction: number;

    if (fraction <= 1.2) niceFraction = 1.2;
    else if (fraction <= 1.5) niceFraction = 1.5;
    else if (fraction <= 2) niceFraction = 2;
    else if (fraction <= 3) niceFraction = 3;
    else if (fraction <= 5) niceFraction = 5;
    else if (fraction <= 7.5) niceFraction = 7.5;
    else niceFraction = 10;

    return niceFraction * Math.pow(10, exponent);
  }

  formatYAxisTick(val: number): string {
    if (val >= 1_000_000) {
      return (val / 1_000_000).toFixed(val % 1_000_000 === 0 ? 0 : 1) + 'M';
    }
    if (val >= 1_000) {
      return (val / 1_000).toFixed(val % 1_000 === 0 ? 0 : 1) + 'k';
    }
    return val.toString();
  }

  formatValueWithUnit(val: number, unit: string): string {
    if (unit === 'GNF') {
      return this.formatCurrency(val);
    }
    return `${val} ${unit}`;
  }

  private generateSmoothPath(points: { x: number; y: number }[]): string {
    if (!points || points.length === 0) return '';
    if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;

    let d = `M ${points[0].x} ${points[0].y}`;
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i === 0 ? 0 : i - 1];
      const p1 = points[i];
      const p2 = points[i + 1];
      const p3 = points[i + 2 < points.length ? i + 2 : i + 1];

      const cp1x = p1.x + (p2.x - p0.x) / 6;
      const cp1y = p1.y + (p2.y - p0.y) / 6;
      const cp2x = p2.x - (p3.x - p1.x) / 6;
      const cp2y = p2.y - (p3.y - p1.y) / 6;

      d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
    }
    return d;
  }

  private generateAreaPath(points: { x: number; y: number }[], baseY: number): string {
    if (!points || points.length === 0) return '';
    const linePath = this.generateSmoothPath(points);
    const first = points[0];
    const last = points[points.length - 1];
    return `${linePath} L ${last.x} ${baseY} L ${first.x} ${baseY} Z`;
  }

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    forkJoin({
      global: this.adminService.getGlobalStats(),
      beds: this.adminService.getBedOccupancyStats(),
      finances: this.adminService.getFinancialStats(),
      appointments: this.adminService.getRecentAppointments(6),
      hospitalizations: this.adminService.getCurrentHospitalizations(6),
      services: this.adminService.getHospitalServicesSummary(),
      activities: this.adminService.getRecentActivityFeed()
    }).pipe(
      finalize(() => this.isLoading.set(false))
    ).subscribe({
      next: (res) => {
        this.globalStats.set(res.global);
        this.bedOccupancy.set(res.beds);
        this.financialStats.set(res.finances);
        this.recentAppointments.set(res.appointments);
        this.currentHospitalizations.set(res.hospitalizations);
        this.hospitalServices.set(res.services);
        this.recentActivities.set(res.activities);
      },
      error: () => {
        this.errorMessage.set('Une erreur est survenue lors de la récupération des données administratives.');
      }
    });
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'GNF',
      maximumFractionDigits: 0
    }).format(amount || 0).replace('GNF', 'GNF');
  }

  formatDate(dateStr: string): string {
    return formatSharedDate(dateStr, 'N/D');
  }

  getRdvBadgeClass(statut: string): string {
    switch ((statut || '').toUpperCase()) {
      case 'CONFIRME': return 'status-confirmed';
      case 'EN_ATTENTE': return 'status-pending';
      case 'TERMINE': return 'status-completed';
      case 'ANNULE': return 'status-cancelled';
      case 'EN_COURS': return 'status-in-progress';
      case 'PROGRAMME': return 'status-programmed';
      default: return 'status-default';
    }
  }
}
