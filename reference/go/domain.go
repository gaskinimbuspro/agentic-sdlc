package main

import (
	"errors"
	"regexp"
	"strings"
	"unicode/utf8"
)

var emailPattern = regexp.MustCompile("^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(\\.[a-z0-9-]+)+$")
var errInvalidInput = errors.New("invalid input")

func customerValues(name, email string) (string, string, error) {
	name, email = strings.TrimSpace(name), strings.ToLower(strings.TrimSpace(email))
	if utf8.RuneCountInString(name) < 1 || utf8.RuneCountInString(name) > 100 || len(email) > 254 || !emailPattern.MatchString(email) {
		return "", "", errInvalidInput
	}
	return name, email, nil
}
