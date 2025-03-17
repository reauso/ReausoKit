from unittest import TestCase

from rkit.string import replace_multiple


class StringTests(TestCase):

    def test_replace_multiple_GivenValidReplacements_ReturnsModifiedString(self):
        result = replace_multiple("hello world", {"hello": "hi", "world": "everyone"})
        self.assertEqual(result, "hi everyone")

    def test_replace_multiple_GivenEmptyReplacements_ReturnsOriginalString(self):
        result = replace_multiple("hello world", {})
        self.assertEqual(result, "hello world")

    def test_replace_multiple_GivenNoMatchingKeys_ReturnsOriginalString(self):
        result = replace_multiple("hello world", {"bye": "goodbye"})
        self.assertEqual(result, "hello world")

    def test_replace_multiple_GivenOverlappingReplacements_AppliesSequentially(self):
        result = replace_multiple("aaa", {"aa": "b", "a": "c"})
        self.assertEqual(result, "bc")  # "aaa" -> "ba" -> "bc"

    def test_replace_multiple_GivenSubstringMatches_ReplacesAllInstances(self):
        result = replace_multiple("abc abc abc", {"abc": "xyz"})
        self.assertEqual(result, "xyz xyz xyz")

    def test_replace_multiple_GivenPartialOverlap_ReplacesAllOccurrences(self):
        result = replace_multiple("banana", {"ban": "can", "na": "ma"})
        self.assertEqual(result, "camama")  # "banana" -> "canana" -> "camama"

    def test_replace_multiple_GivenEmptyString_ReturnsEmptyString(self):
        result = replace_multiple("", {"a": "b"})
        self.assertEqual(result, "")

    def test_replace_multiple_GivenReplacementsWithEmptyString_RemovesMatches(self):
        result = replace_multiple("hello world", {"hello": "", "world": ""})
        self.assertEqual(result, " ")

    def test_replace_multiple_GivenSameKeyAndValue_LeavesStringUnchanged(self):
        result = replace_multiple("hello world", {"hello": "hello", "world": "world"})
        self.assertEqual(result, "hello world")

    def test_replace_multiple_GivenCaseSensitiveReplacements_AppliesOnlyExactMatches(self):
        result = replace_multiple("Hello world", {"hello": "hi", "world": "everyone"})
        self.assertEqual(result, "Hello everyone")  # "Hello" is not replaced since it's case-sensitive
