import { Component, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent, FooterComponent } from './shared/components';
import { HomeComponent } from './features/home/home.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  @ViewChild('homeRef') homeComponent?: HomeComponent;

  onOpenBooking(): void {
    if (this.homeComponent) {
      this.homeComponent.openBooking();
    }
  }

  onOpenPrescription(): void {
    if (this.homeComponent) {
      this.homeComponent.openPrescription();
    }
  }

  onScrollToSection(sectionId: string): void {
    if (this.homeComponent) {
      this.homeComponent.scrollToSection(sectionId);
    } else {
      const el = document.getElementById(sectionId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }
}
