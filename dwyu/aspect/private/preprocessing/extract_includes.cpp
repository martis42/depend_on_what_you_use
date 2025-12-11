#include "dwyu/aspect/private/preprocessing/extract_includes.h"

#include <climits>
#include <istream>
#include <set>
#include <string>

namespace dwyu {
namespace {

class IncludeStatementExtractor {
  public:
    // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init) init function does all initialization
    IncludeStatementExtractor() { init(); }

    void init() {
        ongoing_extraction_ = true;

        checking_preprocessor_statement_ = true;
        expect_next_ = 'i';

        expect_quoting_or_white_space_ = false;

        expect_path_ = false;
        finished_extraction_ = false;
        parsed_include_ = "";
    }

    bool ongoingExtraction() const { return ongoing_extraction_; }
    bool hasValidIncludeStatement() const { return finished_extraction_; }

    std::string getIncludeStatement() const { return parsed_include_; }

    void addChar(const char character) {
        if (checking_preprocessor_statement_) {
            if (character != expect_next_) {
                ongoing_extraction_ = false;
                return;
            }
            switch (character) {
            case 'i':
                expect_next_ = 'n';
                return;
            case 'n':
                expect_next_ = 'c';
                return;
            case 'c':
                expect_next_ = 'l';
                return;
            case 'l':
                expect_next_ = 'u';
                return;
            case 'u':
                expect_next_ = 'd';
                return;
            case 'd':
                expect_next_ = 'e';
                return;
            case 'e':
                checking_preprocessor_statement_ = false;
                expect_quoting_or_white_space_ = true;
                return;
            default:
                // We can never reach here
                expect_next_ = CHAR_MAX;
            }
        }

        if (expect_quoting_or_white_space_ && character == ' ') {
            return;
        }

        if (expect_quoting_or_white_space_ && (character == '"' || character == '<')) {
            expect_quoting_or_white_space_ = false;
            expect_path_ = true;
            return;
        }

        if (expect_path_ && (character == '"' || character == '>')) {
            ongoing_extraction_ = false;
            finished_extraction_ = true;
            return;
        }

        if (expect_path_) {
            parsed_include_ += character;
            return;
        }

        // Reaching here means it is not an include statement
        ongoing_extraction_ = false;
    }

  private:
    bool ongoing_extraction_;

    bool checking_preprocessor_statement_;
    char expect_next_;

    bool expect_quoting_or_white_space_;

    bool expect_path_;
    bool finished_extraction_;
    std::string parsed_include_;
};

} // namespace

std::set<std::string> extractIncludes(std::istream& stream) {
    std::set<std::string> includes{};
    IncludeStatementExtractor include_extractor{};
    bool in_commented_line = false;
    bool in_c_comment_block = false;
    char character{};
    char prev_character{0};
    while (stream.get(character)) {
        if (character == '/' && prev_character == '/' && !in_c_comment_block) {
            in_commented_line = true;
        }
        if ((character == '\n' || character == '\r') && in_commented_line) {
            in_commented_line = false;
        }
        if (character == '*' && prev_character == '/' && !in_commented_line) {
            in_c_comment_block = true;
        }
        if (character == '/' && prev_character == '*') {
            in_c_comment_block = false;
        }

        prev_character = character;

        if (in_commented_line || in_c_comment_block) {
            continue;
        }

        if (character == '#') {
            include_extractor.init();
            continue;
        }

        if (include_extractor.ongoingExtraction()) {
            include_extractor.addChar(character);
        }
        else {
            continue;
        }

        if (include_extractor.hasValidIncludeStatement()) {
            includes.insert(include_extractor.getIncludeStatement());
        }
    }

    return includes;
}

} // namespace dwyu
