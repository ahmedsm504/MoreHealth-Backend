

### **1. Groups Endpoint** (`/groups/`)
**HTTP Methods**: GET, POST 

#### **Filter Parameters**:
| Parameter | Example | Description |
|-----------|---------|-------------|
| `tags` | `?tags=python,web` | Filter by exact tag matches (comma-separated) |
| `created_after` | `?created_after=2023-01-01` | Groups created after date (YYYY-MM-DD) |
| `created_before` | `?created_before=2023-12-31` | Groups created before date |
| `min_members` | `?min_members=10` | Groups with ≥ X members |
| `creator` | `?creator=admin` | Groups created by specific username |
| `member` | `?member=john` | Groups containing specific member |
| `my_groups` | `?my_groups=true` | Groups the current user has joined |
| `name` | `?name=Python` | Exact name match |
| `name__icontains` | `?name__icontains=dev` | Case-insensitive partial name match |
| `tag_search` | `?tag_search=py` | Partial tag name match |

#### **Search** (`search`):
```http
GET /groups/?search=web
```
Searches in:
- Group names
- Descriptions
- Tag names
- Creator usernames

#### **Ordering** (`ordering`):
```http
GET /groups/?ordering=-members_count
```
Options: `created_at`, `name`, `members_count` (add `-` for descending)

### delet or update  /groups/num

---

### **2. Group Questions** (`/groups/<group_pk>/questions/`)
**HTTP Methods**: GET, POST

#### **Parameters**:
| Parameter | Example | Description |
|-----------|---------|-------------|
| `search` | `?search=django` | Search in question titles/content |
| `ordering` | `?ordering=-created_at` | Order by `created_at`, `title` |
| `user` | `?user=john` | Filter by author username |

---

### **3. Question Comments** (`/questions/<question_pk>/comments/`)
**HTTP Methods**: GET, POST

#### **Parameters**:
| Parameter | Example | Description |
|-----------|---------|-------------|


---

### **4. Upvotes** (`/upvote/<model_type>/<pk>/`)
**HTTP Methods**: POST  
**Parameters**: Automatic based on URL pattern
```http
POST /upvote/question/5/
POST /upvote/comment/12/
```

---

### **5. Membership** (`/groups/<pk>/join/`)
**HTTP Methods**: POST  
**Parameters**: None (uses authenticated user)

---

### **6. User-Specific Filters**
For any endpoint requiring authentication:
```http
Authorization: Token your_token_here
```

---

### **Combination Examples**
1. **Complex Group Search**:
   ```http
   GET /groups/?tags=python&min_members=5&created_after=2023-01-01&ordering=-members_count
   ```

2. **Personalized Feed**:
   ```http
   GET /groups/?my_groups=true&ordering=-created_at
   ```

3. **Full-Text Search**:
   ```http
   GET /questions/?search="error handling"&ordering=-upvotes
   ```

---

### **Special Notes**
1. Date formats: Always use `YYYY-MM-DD`
2. Multiple values: Comma-separated (`tags=python,django`)
3. Authentication: Required for write operations
4. Error responses: Check for 400/403 status codes with error details

Would you like me to explain any specific parameter or scenario in more detail?



GET /groups/?tags=python,web&min_members=10&ordering=-members_count




Here's a comprehensive list of all filter parameters available in your API endpoints, organized by resource:

---

### **1. Groups Endpoint** (`/groups/`)
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `tags` | string | `?tags=python,django` | Filter by exact tag matches (comma-separated) |
| `tag_search` | string | `?tag_search=web` | Partial match for tag names |
| `created_after` | date | `?created_after=2023-01-01` | Groups created after date (YYYY-MM-DD) |
| `created_before` | date | `?created_before=2023-12-31` | Groups created before date |
| `min_members` | integer | `?min_members=5` | Groups with ≥ X members |
| `creator` | string | `?creator=admin` | Filter by creator's username |
| `member` | string | `?member=john` | Groups containing specific member |
| `my_groups` | boolean | `?my_groups=true` | Groups the current user has joined |
| `name` | string | `?name=Python%20Club` | Exact name match |
| `name__icontains` | string | `?name__icontains=dev` | Case-insensitive partial name match |
| `search` | string | `?search=programming` | Full-text search (name, description, tags) |
| `ordering` | string | `?ordering=-members_count` | Sort results (`created_at`, `name`, `members_count`) |

---

### **2. Questions Endpoint** (`/groups/<group_pk>/questions/`)
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `search` | string | `?search="error handling"` | Search in titles and content |
| `user` | string | `?user=sara` | Filter by author's username |
| `created_after` | date | `?created_after=2023-06-01` | Questions created after date |
| `ordering` | string | `?ordering=-upvotes_count` | Sort by `created_at`, `upvotes_count` |
| `has_comments` | boolean | `?has_comments=true` | Questions with comments (if implemented) |

---
