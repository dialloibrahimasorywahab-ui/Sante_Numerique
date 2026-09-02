import { Component, output } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';

@Component({
  selector: 'app-public-layout',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent],
  template: '<app-header (openBookingModal)="openBookingModal.emit()" (openPrescriptionModal)="openPrescriptionModal.emit()" (scrollToSection)="scrollToSection.emit($event)"></app-header><main><router-outlet></router-outlet></main><app-footer (scrollToSection)="scrollToSection.emit($event)"></app-footer>'
})
export class PublicLayoutComponent {
  openBookingModal = output<void>();
  openPrescriptionModal = output<void>();
  scrollToSection = output<string>();
}
