import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-personnel-profil',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './personnel-profil.component.html',
  styleUrl: './personnel-profil.component.scss'
})
export class PersonnelProfilComponent {
  authService = inject(AuthService);
}
