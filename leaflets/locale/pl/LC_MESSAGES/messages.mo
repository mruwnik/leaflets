��    [      �     �      �  4   �     �               /     D     Z     p     �     �     �  O   �  *   	  *   G	  d   r	     �	     �	     �	     �	     
     
     *
     >
     S
     j
     |
     �
     �
  	   �
     �
     �
     �
     �
     �
     �
     �
          
          '     ;     @     M     ^  
   |     �     �     �     �     �     �     �     �     �     �     �                    /     8     @     M     V     _     o     ~     �     �     �     �     �  	   �     �     �  
                    &   %     L     \     a     p     �     �     �  	   �     �     �  �   �  M   _     �     �  !   �     �     �          ,     K  %   k     �  [   �  '     5   /  �   e  
   �     �            !   .  0   P     �  0   �     �     �     �  )   
     4  
   E     P     f     k     {     �     �     �     �     �     �     �     	  
             )     H     \  1  s  �  �     Z     `  
   q     |     �     �     �     �     �     �     �     �     �            	   &     0     C  8   R     �  K   �     �     �     �          "  3   5     i     �  .   �     �     �     �     �                  #   .  
   R     ]     p  
   }     T       ;       9             )      5   -                    2                   R   P      E       Y      6      %   
          :      O                    D   (      8                   /   S      J       V                   F         $   Z             7   	   K   U      M   ,   =   B   !   #   [   3                     G   Q   1       N       H       >   "             <   .   0          4               C   '   ?   L          W   I   +   &       *   @   A   X           "lat", "lon", "town", "postcode", "street", "house". CSV file to import Click Import by map selection Import from CSV file No addresses selected No selection provided No such address found No such campaign found No user id provided The passwords do not match The provided file should be a tab delimited CSV file with the following columns There already is a campaign with this name There already is a user with that username You can only select a limited area at once, so if you choose too large an area, an error will appear actions add user add_campaign assign_addresses assign_campaign assigned_child_user assigned_other_user assigned_parent_user assigned_selected_user bad bounding args bad_parent_provided bad_user_ids campaign_name campaigns children_campaigns country description deselect_area edit edit_campaign email emails emails_missing example_email for an example file here house_number import_addresses invalid coordinartes provided invitation invite users invite_emails_explaination invite_invite_explaination is_admin is_equal lat login logout lon manage_users mr smith no bounding box parent parent_campaigns password pending pending_user postcode preview: repeat_password reset_password reset_password_email reset_password_subject sample_invitation save select_area show_campaign show_list show_map stale_activation_link start_date street subject submit the provided bounding box is too large toggle_selector town track_position unassigned_address unvisited_address url_macro_missing user_campaigns user_name users visited_address Project-Id-Version: 0.1
Last-Translator: Daniel O'Connell <tojad99@gmail.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
 "Wysokość", "Szerokość", "Miasto", "Kod pocztowy", "Ulica", "Nr budynku". Podaj plik CSV Kliknij Wycztaj poprzez wybieranie z mapy Wczytaj z pliku CSV Nie wybrano żadnych adresów Niczego nie wybrano Nie odnaleziona takiego adresu Nie odnależono takiej kampanii Nie podano identyfikator użytkownika Hasła nie są takie same Podany plik powinien być plikiem CSV mając następujące kolumny rozdzielone tabulatorami Już istnieje wydarzenie z taką nazwą Już istnieje użytkownik z taką nazwą użytkownika Na raz można tylko wczytać ograniczony obszar, więc jeżeli zbyt duży obszar zostanie wybrany, wyświetli się komunikat błędu Czynności Dodaj użytkownika Dodaj nowe wydarzenie Przypisz adresy Przypisz adresy do użytkowników Podrzędnego użytkownika wybranego użytkownika Innego użytkownika Nadrzędnego użytkownika wybranego użytkownika Wybranego użytkownika Podano błędny obszar Podano złego rodzica Podano złe identyfikatory użytkowników Nazwa wydarzenia Wydarzenia Wydarzenia podrzędne Kraj Opis wydarzenia Odznacz obszar Edycja Edytuj wydarzenie Email Adresy mailowe Nie podano poprawnych adresów. z.ciebie@jest.com by zobaczyć przykładowy plik tutaj Nr budynku Wczytaj adresy Podano błędne współrzędne Treść zaproszenia zaprosz użytkowników Podaj listę adresów mailowych do zaproszenia. Jeżeli już istnieje użytkownik z podanym adresem, zostanie on pominięty. Adresy powinny być w formacie "{nazwa użytkownika} &lt;{address mailowy}&gt;" albo sam adres. Podając wiele adresów, należy je rozdzielać średnikami, przecinkami lub w osobnych wieszach. Poniżej jest przykładowa lista adresów;<br><br><textarea rows=4 cols=90 readonly>a <a@b.com>, b <b@b.com>, Pan Tarei &lt;woda@rzeka.org&gt; ; jozef@gmail.com; Lucia &lt;afryka@gleba.com&gt;
janek@gdzies.com

karol@fe.org</textarea><br><br> Tutaj należy wpisać treść zaproszenia który zostanie przesłany do wszystkich podanych adresów. Są dostępne szablony, które zostaną podmienione właściwymi wartości w wysłanej wiadomości:<br> - {name} - nazwa podane przy adresie mailowy<br> - {email} - adres mailowy na który zostanie wiadomość wysłana<br> - {url} - strona na którą należy wejść by aktywować nowe konto (ta wartość jest wymagane w wiadomości) Admin Równouprawniony Wysokość Zaloguj Wyloguj Szerokość Zarządzaj użytkownikami Anna Kowalska Nie podano obszaru Grupa Wydarzenia nadrzędne Hasło W trakcie aktualizacji nie aktywny Kod pocztowy Podgląd: Powtórzone hasło Wykasuj hasło Aby ponownie ustawić hasło, należy kliknąć na {url} Zmiana hasła Witaj {name}
  proszę potwierzić swoje konto wchodząc na {url}
  Dzięki Zapisz Zaznacz obszar Pokaż wydarzenie Wyświetl jako lista Wyświetl na mapie Ten odnośnik się przeterminował. Poproś o nowy. Data rozpoczęcia wydarzenia Ulica Podaj temat dla maila który zostanie wysłany Wyślij Podany obszar jest zbyt duży Ukryj/pokaż zaznacznika Miasto Pokaż pozycję Nie przypisany Nieodwiedzone Wyamagane jest {url} w wiadomości. Wydarzenia Nazwa użytkownika Użytkownicy Odwiedzone 