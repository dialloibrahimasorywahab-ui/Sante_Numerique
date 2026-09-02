import { Component } from '@angular/core';
import { PublicLayoutComponent } from './layout/public-layout/public-layout.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [PublicLayoutComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class App {
  onOpenBooking(): void {
    document.getElementById('booking')?.scrollIntoView({ behavior: 'smooth' });
  }

  onOpenPrescription(): void {
    document.getElementById('prescription')?.scrollIntoView({ behavior: 'smooth' });
  }

  onScrollToSection(sectionId: string): void {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
}
