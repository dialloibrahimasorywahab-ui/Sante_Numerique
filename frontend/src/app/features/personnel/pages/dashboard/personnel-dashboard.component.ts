import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PersonnelService } from '../../services/personnel.service';
import { PersonnelDashboardMetrics } from '../../models/personnel.model';

@Component({
  selector: 'app-personnel-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './personnel-dashboard.component.html',
  styleUrl: './personnel-dashboard.component.scss'
})
export class PersonnelDashboardComponent implements OnInit {
  private personnelService = inject(PersonnelService);

  isLoading = signal<boolean>(true);
  metrics = signal<PersonnelDashboardMetrics | null>(null);

  ngOnInit(): void {
    this.loadMetrics();
  }

  loadMetrics(): void {
    this.isLoading.set(true);
    this.personnelService.getDashboardMetrics().subscribe({
      next: (data: PersonnelDashboardMetrics) => {
        this.metrics.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.metrics.set(null);
        this.isLoading.set(false);
      }
    });
  }
}
