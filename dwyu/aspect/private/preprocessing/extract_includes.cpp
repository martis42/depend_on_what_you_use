#include "dwyu/aspect/private/preprocessing/extract_includes.h"

#include <limits.h>

namespace dwyu {
namespace {

class IncludeStatementExtractor {
  public:
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

    bool ongoingExtraction() { return ongoing_extraction_; }
    bool hasValidIncludeStatement() { return finished_extraction_; }

    std::string getIncludeStatement() { return parsed_include_; }

    void addChar(const char c) {
        if (checking_preprocessor_statement_) {
            if (c != expect_next_) {
                ongoing_extraction_ = false;
                return;
            }
            else {
                switch (c) {
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
        }

        if (expect_quoting_or_white_space_ && c == ' ') {
            return;
        }

        if (expect_quoting_or_white_space_ && (c == '"' || c == '<')) {
            expect_quoting_or_white_space_ = false;
            expect_path_ = true;
            return;
        }

        if (expect_path_ && (c == '"' || c == '>')) {
            ongoing_extraction_ = false;
            finished_extraction_ = true;
            return;
        }

        if (expect_path_) {
            parsed_include_ += c;
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
    char c{};
    char pc{0};
    while (stream.get(c)) {
        if (c == '/' && pc == '/' && !in_c_comment_block) {
            in_commented_line = true;
        }
        if ((c == '\n' || c == '\r') && in_commented_line) {
            in_commented_line = false;
        }
        if (c == '*' && pc == '/' && !in_commented_line) {
            in_c_comment_block = true;
        }
        if (c == '/' && pc == '*') {
            in_c_comment_block = false;
        }

        pc = c;

        if (in_commented_line || in_c_comment_block) {
            continue;
        }

        if (c == '#') {
            include_extractor.init();
            continue;
        }

        if (include_extractor.ongoingExtraction()) {
            include_extractor.addChar(c);
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
