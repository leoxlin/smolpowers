import unittest

from app import create_app


class LinkShortenerApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_app({"TESTING": True}).test_client()

    def test_create_list_and_follow_link(self) -> None:
        created = self.client.post("/links", json={"url": "https://example.com/article"})

        self.assertEqual(created.status_code, 201)
        link = created.get_json()
        self.assertEqual(link["url"], "https://example.com/article")
        self.assertEqual(self.client.get("/links").get_json(), [link])

        followed = self.client.get(f"/{link['code']}")
        self.assertEqual(followed.status_code, 302)
        self.assertEqual(followed.headers["Location"], "https://example.com/article")

    def test_delete_link(self) -> None:
        link = self.client.post("/links", json={"url": "https://example.com"}).get_json()

        self.assertEqual(self.client.delete(f"/links/{link['code']}").status_code, 204)
        self.assertEqual(self.client.get(f"/{link['code']}").status_code, 404)

    def test_rejects_missing_url(self) -> None:
        response = self.client.post("/links", json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "url is required"})


if __name__ == "__main__":
    unittest.main()
