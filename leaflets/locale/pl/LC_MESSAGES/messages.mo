��    T      �  q   \         4   !     V     i     o     �     �     �     �     �     �     	  O   $  *   t  *   �  d   �     /	     7	     @	     M	     ]	     q	     �	     �	     �	     �	     �	     �	  	   �	     �	     
     
     #
     1
     ?
     E
     L
     [
     i
     }
     �
     �
     �
  
   �
     �
     �
     �
                    "     (     /     3     @     I     Y     j     s     {     �     �     �     �     �     �     �  	   �     �     �  
                    &   %     L     \     a     p     �     �     �  	   �     �  �   �  M   Y     �     �  !   �     �     �          &     E  %   e     �  [   �  $     5   &  �   \  
   �     �     �  #     0   9     j  0   ~     �     �     �  )   �          +     4     H     M     Z     i     z     �     �     �     �     �  
   �     �                3  1  J  �  |     1     7  
   H     S     [     c     o     �     �     �     �     �     �     �  	   �     �  K        ^     e     t     �     �  3   �     �     �  .        0     8     V     o     v     �     �  #   �     �     �  
   �     #   8   	         &              @   4       B              6   $                  E   L   G      .       9                           A   7   -   
   5   <   S   :   0      Q       2      1   ,   T             =   P   C                 F   +   )          R   (   I       /          D   !      J              K           N   "                           %   *       3   O   ?      ;                    '   >   M   H        "lat", "lon", "town", "postcode", "street", "house". CSV file to import Click Import by map selection Import from CSV file No addresses selected No selection provided No such address found No such campaign found No user id provided The passwords do not match The provided file should be a tab delimited CSV file with the following columns There already is a campaign with this name There already is a user with that username You can only select a limited area at once, so if you choose too large an area, an error will appear actions add user add_campaign assign_campaign assigned_child_user assigned_other_user assigned_parent_user assigned_selected_user bad bounding args bad_parent_provided bad_user_ids campaign_name campaigns children_campaigns country description deselect_area edit_campaign email emails emails_missing example_email for an example file here house_number import_addresses invalid coordinartes provided invitation invite users invite_emails_explaination invite_invite_explaination is_admin is_equal lat login logout lon manage_users mr smith no bounding box parent_campaigns password pending pending_user postcode preview: repeat_password sample_invitation save select_area show_campaign show_list show_map stale_activation_link start_date street subject submit the provided bounding box is too large toggle_selector town track_position unassigned_address unvisited_address url_macro_missing user_campaigns user_name visited_address Project-Id-Version: 0.1
Last-Translator: Daniel O'Connell <tojad99@gmail.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
 "Wysokość", "Szerokość", "Miasto", "Kod pocztowy", "Ulica", "Nr budynku". Podaj plik CSV Kliknij Wycztaj poprzez wybieranie z mapy Wczytaj z pliku CSV Nie wybrano żadnych adresów Niczego nie wybrano Nie odnaleziona takiego adresu Nie odnależono takiej kampanii Nie podano identyfikator użytkownika Hasła nie są takie same Podany plik powinien być plikiem CSV mając następujące kolumny rozdzielone tabulatorami Już istniej kampania z taką nazwą Już istnieje użytkownik z taką nazwą użytkownika Na raz można tylko wczytać ograniczony obszar, więc jeżeli zbyt duży obszar zostanie wybrany, wyświetli się komunikat błędu Czynności Dodaj użytkownika Dodaj nową kampanię Przypisz użytkowników do adresów Podrzędnego użytkownika wybranego użytkownika Innego użytkownika Nadrzędnego użytkownika wybranego użytkownika Wybranego użytkownika Podano błędny obszar Podano złego rodzica Podano złe identyfikatory użytkowników Nazwa kampani Kampanie Kampanie podrzędne Kraj Opis kampani Odznacz obszar Edytuj kampanię Email Adresy mailowe Nie podano poprawnych adresów. z.ciebie@jest.com by zobaczyć przykładowy plik tutaj Nr budynku Wczytaj adresy Podano błędne współrzędne Treść zaproszenia zaprosz użytkowników Podaj listę adresów mailowych do zaproszenia. Jeżeli już istnieje użytkownik z podanym adresem, zostanie on pominięty. Adresy powinny być w formacie "{nazwa użytkownika} &lt;{address mailowy}&gt;" albo sam adres. Podając wiele adresów, należy je rozdzielać średnikami, przecinkami lub w osobnych wieszach. Poniżej jest przykładowa lista adresów;<br><br><textarea rows=4 cols=90 readonly>a <a@b.com>, b <b@b.com>, Pan Tarei &lt;woda@rzeka.org&gt; ; jozef@gmail.com; Lucia &lt;afryka@gleba.com&gt;
janek@gdzies.com

karol@fe.org</textarea><br><br> Tutaj należy wpisać treść zaproszenia który zostanie przesłany do wszystkich podanych adresów. Są dostępne szablony, które zostaną podmienione właściwymi wartości w wysłanej wiadomości:<br> - {name} - nazwa podane przy adresie mailowy<br> - {email} - adres mailowy na który zostanie wiadomość wysłana<br> - {url} - strona na którą należy wejść by aktywować nowe konto (ta wartość jest wymagane w wiadomości) Admin Równouprawniony Wysokość Zaloguj Wyloguj Szerokość Zarządzaj użytkownikami Anna Kowalska Nie podano obszaru Kampanie nadrzędne Hasło W trakcie aktualizacji nie aktywny Kod pocztowy Podgląd: Powtórzone hasło Witaj {name}
  proszę potwierzić swoje konto wchodząc na {url}
  Dzięki Zapisz Zaznacz obszar Pokaż kampanię Wyświetl jako lista Wyświetl na mapie Ten odnośnik się przeterminował. Poproś o nowy. Data rozpoczęcia kampani Ulica Podaj temat dla maila który zostanie wysłany Wyślij Podany obszar jest zbyt duży Ukryj/pokaż zaznacznika Miasto Śledź pozycję Nie przypisane Nieodwiedzone Wyamagane jest {url} w wiadomości. Kampanie Nazwa użytkownika Odwiedzone 