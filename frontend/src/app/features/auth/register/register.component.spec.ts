import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { RegisterComponent } from './register.component';

describe('RegisterComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegisterComponent],
      providers: [
        provideRouter([]),
        provideHttpClient()
      ]
    }).compileComponents();
  });

  it('should create the register component', () => {
    const fixture = TestBed.createComponent(RegisterComponent);
    const component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });

  it('should detect password mismatch', () => {
    const fixture = TestBed.createComponent(RegisterComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;

    component.registerForm.setValue({
      prenom: 'Fatimatou',
      nom: 'Diallo',
      email: 'fatimatou@example.com',
      telephone: '+224620123456',
      login: 'fatimatou_d',
      motDePasse: 'Password123!',
      confirmationMotDePasse: 'Different123!'
    });

    expect(component.registerForm.valid).toBe(false);
    expect(component.registerForm.hasError('passwordMismatch')).toBe(true);
  });
});
