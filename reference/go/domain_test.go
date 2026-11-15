package main

import "testing"

func TestCustomerValues(t *testing.T) {
	name, email, err := customerValues(" Ada ", " ADA@EXAMPLE.TEST ")
	if err != nil || name != "Ada" || email != "ada@example.test" {
		t.Fatal("normalization failed")
	}
	for _, tc := range []struct{ name, email string }{{"", "a@b.test"}, {"Ada", "invalid"}, {"Ada", "a@b"}} {
		if _, _, err := customerValues(tc.name, tc.email); err == nil {
			t.Errorf("accepted invalid input: %q", tc.name)
		}
	}
}
