
## Retrieve Object Collection

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/metadata/vobjects?loc=true
```

### Response

```json
{
  "responseStatus": "SUCCESS",
  "objects": [
    {
       "url": "/api/v24.3/metadata/vobjects/user__sys",
       "label": "User",
       "name": "user__sys",
       "label_plural": "Users",
       "prefix": "V0A",
       "order": 87,
       "in_menu": true,
       "source": "system",
       "status": [
           "active__v"
       ],
       "configuration_state": "STEADY_STATE",
       "localized_data": {
           "label_plural": {
               "de": "Benutzer",
               "ru": "Пользователи",
               "sv": "Användare",
               "kr": "사용자",
               "en": "Users",
               "pt_BR": "Usuários",
               "it": "Utenti",
               "fr": "Utilisateurs",
               "hu": "Felhasználók",
               "es": "Usuarios",
               "zh": "用户",
               "zh_TW": "使用者",
               "th": "ผู้ใช้",
               "ja": "ユーザ",
               "pl": "Użytkownicy",
               "tr": "Kullanıcılar",
               "nl": "Gebruikers",
               "pt_PT": "Utilizadores"
           },
           "label": {
               "de": "Benutzer",
               "ru": "Пользователь",
               "sv": "Användare",
               "kr": "사용자",
               "en": "User",
               "pt_BR": "Usuário",
               "it": "Utente",
               "fr": "Utilisateur",
               "hu": "Felhasználó",
               "es": "Usuario",
               "zh": "用户",
               "zh_TW": "使用者",
               "th": "ผู้ใช้",
               "ja": "ユーザ",
               "pl": "Użytkownik",
               "tr": "Kullanıcı",
               "nl": "Gebruiker",
               "pt_PT": "Utilizador"
           }
       }
    },
    {
       "url": "/api/v24.3/metadata/vobjects/country__v",
       "label": "Country",
       "name": "country__v",
       "label_plural": "Countries",
       "prefix": "00C",
       "in_menu": true,
       "source": "standard",
       "status": [
           "active__v"
       ],
       "configuration_state": "STEADY_STATE",
       "localized_data": {
           "label_plural": {
               "de": "Länder",
               "ru": "Страны",
               "sv": "Länder",
               "kr": "국가",
               "en": "Countries",
               "it": "Paesi",
               "pt_BR": "Países",
               "fr": "Pays",
               "hu": "Országok",
               "es": "Países",
               "zh": "国家/地区",
               "zh_TW": "國家/地區",
               "th": "ประเทศ",
               "ja": "国",
               "pl": "Kraje",
               "tr": "Ülkeler",
               "nl": "Landen",
               "pt_PT": "Países"
           },
           "label": {
               "de": "Land",
               "ru": "Страна",
               "sv": "Land",
               "kr": "국가",
               "en": "Country",
               "it": "Paese",
               "pt_BR": "País",
               "fr": "Pays",
               "hu": "Ország",
               "es": "País",
               "zh": "国家/地区",
               "zh_TW": "國家/地區",
               "th": "ประเทศ",
               "ja": "国",
               "pl": "Kraj",
               "tr": "Ülke",
               "nl": "Land",
               "pt_PT": "País"
           }
       }
    }
  ]
}
```

Retrieve all Vault objects in the authenticated Vault.

**Endpoint:** `GET /api/{version}/metadata/vobjects`

### Headers

| Name | Description |
| ---- | ----------- |
| Accept | application/json (default) or application/xml |

### Query Parameters

| Name | Description |
| ---- | ----------- |
| loc | Set to true to retrieve localized (translated) strings for the label and label_plural object fields. If omitted, defaults to false and localized Strings are not included. |

### Response Details

The response includes a summary of key information (url, label, name, prefix, status, etc.) for all standard and custom Vault Objects configured in your Vault.

| Name | Description |
| ---- | ----------- |
| localized_data | When loc=true, this array contains translated field labels for each object. This data is only available at the object and field level, and only if localized Strings have been configured on objects in your Vault. |
| configuration_state | The configuration state of your raw object.**STEADY_STATE**: This object has no pending configuration changes.**IN_DEPLOYMENT**: This object has queued or in-progress configuration changes. While in this state, Vault Admins cannot make further edits to the object configuration, and Vault users continue to interact with the Active object configuration version. In this state, you may also cancel deployment. |
