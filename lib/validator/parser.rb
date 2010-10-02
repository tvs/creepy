module Parser
  class OutOfBoundsError < Exception; end
  class XML_Comment_Error < Exception; end
  class XML_PI_Error < Exception; end
  class XML_Reserved_Name < Exception; end
  class XML_Syntax_Error < Exception; end
  class XML_Document_Empty < Exception; end
  class XML_Unknown_Version < Exception; end

  class Parser
    XML_DEFAULT_VERSION = "1.0"
    # XML Parser based heavily from libxml2
    # TODO: readers
    attr_accessor :index, :eof_index, :content, :line
    
    def initialize(file)
      @line = 0
      @index = 0
      @file = file
      @content = File.read(file)
      @eof_index = @content.length - 1
    end
  
  
    # TODO: PRIVATIZE
    # Returns the current character in the string
    # TODO: Find a better place to make this check. Having to check each query is expensive
    def cur
      if @index > @eof_index
        raise OutOfBoundsError, "Index #{index} out of bounds" 
        return nil
      end
      @content[@index].chr
    end
  
    # Returns the current + i'th character in the string
    # TODO: Find a better place to make this check. Having to check each query is expensive
    def nxt(i)
      if @index + i > @eof_index
        raise OutOfBoundsError, "Index #{@index+i} out of bounds"
        return nil
      end
      @content[@index+i].chr
    end
  
    # Compares the string character-by-character from the current index with another string.
    # Slices the content from @index...@index+str.length
    # i.e. 
    #   "helloworld".cmp("hello") => true
    #   "hel".cmp("hello") => false
    #
    def cmp(str)
      slc = @content.slice(@index...@index+str.length)
      slc == str
    end
  
    # Skips the index forward i number of characters
    def skip(i=1)
      # Looping so we can track line numbers. Maybe we should just add i.
      i.times { @index += 1; @line += 1 if cur == "\n" }
    end
    
    # skip_blanks
    # skip XML whitespace
    #
    # [3] S ::= (#x20 | #x9 | #xD | #xA)+
    #
    def skip_blanks
      while is_blank?
        skip
      end
    end
    
    # is_blank?
    # returns true if cur is a blank char
    def is_blank?
      is_blank_char?(cur)
    end
    
    # is_blank_char?
    # returns true if char is a blank
    def is_blank_ch?(c)
      return c == 0x20 || c == 0x9 || c == 0xD || c == 0xA
    end
    
    # is_char?
    # returns true if cur is a valid char
    def is_char?
      c = cur[0]
      return (((0x9 <= (c)) && ((c) <= 0xA)) || ((c) == 0xD) || (0x20 <= (c)))
    end
    
    # move_to_end_tag
    # Moves the current index until it reaches a '>'
    def move_to_end_tag
      while (cur != '>'); skip; end
    end
    
    # xmlParseComment
    # Skip an XML comment
    # For compatibility, the string "--" (double-hyphen) must not occur within comments.
    #
    # [15] Comment ::= '<!--' ((Char - '-') | ('-' (Char - '-')))* '-->'
    #
    def xmlParseComment()
      return unless cmp('<!--') # Check that there is a comment right here
      skip(4)
      begin
        until (cmp("-->"))
          raise XML_Comment_Error, "line #{@line}: '--' must not occur within comments" if cmp("--")
          skip # Skip forward until we find a closing brace
        end
        skip(3) # Skip the "-->"
      rescue OutOfBoundsError
        raise XML_Comment_Error, "Comment not terminated"
      end
    end
  
    # xmlParsePI
    # parse an XML processing instruction
    #
    # [16] PI ::= '<?' PITarget (S (Char* - (Char* '?>' Char*)))? '?>'
    #
    def xmlParsePI()
      if (cmp('<?')) # Verify that we're entering a PI
        skip(2)
        target = xmlParsePITarget()
        
        raise XML_Syntax_Error, "line #{@line}: PI #{target}, whitespace expected" if !is_blank?
        
        skip_whitespace()
        begin
          while (is_char? && !cmp("?>"))
            skip
          end
          skip(2) # Skip the "?>"
        rescue OutOfBoundsError
          raise XML_PI_Error, "PI #{target} never terminated"
        end
      end
    end
    
    # xmlParsePITarget
    # parse the name of a PI
    # 
    # [17] PITarget ::= Name - (('X' | 'x') ('M' | 'm') ('L' | 'l'))
    #
    def xmlParsePITarget()
      name = xmlParseName()
      if (!name.nil? && name.downcase.slice(0..2) == "xml")
        if name.length > 3
          raise XML_Reserved_Name, "line #{@line}: Invalid name prefix 'xml'"
        else
          raise XML_Reserved_Name, "line #{@line}: XML declaration only allowed at the start of the document"
        end
      end
      
      if (name.include?(":"))
        raise XML_Syntax_Error, "line #{@line}: Colons are forbidden from PI names:\n #{@line}: '#{name}'"
      end
      return name
    end
    
    # xmlParseName
    # parse an XML name.
    #
    # [4] NameChar ::= Letter | Digit | '.' | '-' | '_' | ':' |
    #                  CombiningChar | Extender
    #
    # [5] Name ::= (Letter | '_' | ':') (NameChar)*
    #
    # [6] Names ::= Name (#x20 Name)*
    #
    # Returns the Name parsed or NULL
    def xmlParseName()
      c = cur[0]
      if (((c >= 0x61) && (c <= 0x7A)) || ((c >= 0x41) && (c <= 0x5A)) || 
         (c == '_') || (c == ':')) then
         
        i = 0
        while (((c >= 0x61) && (c <= 0x7A)) || ((c >= 0x41) && (c <= 0x5A)) ||
       	       ((c >= 0x30) && (c <= 0x39)) || (c == '_') || (c == '-') ||
       	       (c == ':') || (c == '.'))
       	  i += 1
       	  c = nxt(i)[0]
       	  puts i, c.chr
     	  end
     	  
     	  if ((c > 0) && (c < 0x80))
     	    count = i - @index
     	    s = @content.slice(@index...@index+i)
     	    skip(i)
     	    return s
   	    end  
    	end 
    	return nil
    end
    
    # xmlParseTextDecl
    # parse an XML declaration header for external entities
    #
    # [77] TextDecl ::= '<?xml' VersionInfo? EncodingDecl S? '?>'
    #
    def xmlParseTextDecl()
      if (cmp("<?xml"))
        skip(5)
        raise XML_Syntax_Error, "line #{@line}: whitespace expected after '<?xml'" if !is_blank?
        
        skip_blanks
        version = xmlParseVersionInfo()
        version = XML_DEFAULT_VERSION if version.nil?
        raise XML_Syntax_Error, "line #{@line}: whitespace expected after version declaration" if !is_blank?
        
        encoding = xmlParseEncodingDecl()
        raise XML_Syntax_Error, "line #{@line}: missing encoding in text declaration" if encoding.nil?
        
        skip_blanks
        if (cmp('?>'))
          skip(2)
        elsif (cmp('>'))
          raise XML_Syntax_Error, "xml declaration not finished"
          skip
        else
          raise XML_Syntax_Error, "xml declaration not finished"
          move_to_end_tag
          skip
        end
      end
    end
    
    # xmlParseXMLDecl
    # parse an XML declaration header for external entities
    #
    # [23] XMLDecl ::= '<?xml' VersionInfo EncodingDecl? SDDecl? S? '?>'
    #
    def xmlParseXMLDecl()
      if (cmp("<?xml"))
        skip(5)
        raise XML_Syntax_Error, "line #{@line}: whitespace expected after '<?xml'" if !is_blank?
        
        skip_blanks
        version = xmlParseVersionInfo()
        raise XML_Syntax_Error, "line #{@line}: missing version in xml declaration"
        raise XML_Unknown_Version, "unsupported version: '#{version}'" if version != XML_DEFAULT_VERSION
        
        encoding = xmlParseEncodingDecl()
        
        skip_blanks
        if (cmp('?>'))
          skip(2)
        elsif (cmp('>'))
          raise XML_Syntax_Error, "xml declaration not finished"
          skip
        else
          raise XML_Syntax_Error, "xml declaration not finished"
          move_to_end_tag
          skip
        end
      end
    end
    
    # xmlParseVersionInfo
    # parse the XML version
    #
    # [24] VersionInfo ::= S 'version' Eq (' VersionNum ' | " VersionNum ")
    #
    # [25] Eq ::= S? '=' S?
    #
    # Returns the version string or nil
    def xmlParseVersionInfo()
      skip_blanks
      version = nil
      if (cmp("version"))
        skip(7)
        skip_blanks
        
        raise XML_Syntax_Error, "line #{@line}: '=' expected after 'version'" if (cur != '=')
        skip # Skip the '='
        skip_blanks
        
        if (cur == "\"")
          skip # Skip the '\""
          version = xmlParseVersionNum()
          raise XML_Syntax_Error, "version number string not closed" if (cur != "\"")
          skip
        elsif (cur == "\'")
          skip # skip the "\'"
          version = xmlParseVersionNum()
          raise XML_Syntax_Error, "version number string not closed" if (cur != "\'")
          skip
        else
          raise XML_Syntax_Error, "line #{@line}: Version number string not started, expected \" or \'"
        end
      end
      return version
    end
    
    # xmlParseVersionNum
    # parse the XML version value.
    # 
    # [26] VersionNum ::= '1.' [0-9]+
    # 
    # In practice allow [0-9].[0-9]+ at that level
    # 
    # Returns the string giving the XML version number, or nil
    def xmlParseVersionNum()
      version = ""
      c = cur
      if (!((c >= '0') && (c <= '9')))
        raise XML_Syntax_Error, "line #{@line}: Major version number expected [0-9]"
        return nil
      end
      version << c
      skip # Skip the major version
      
      if (!cur == '.')
        raise XML_Syntax_Error, "line #{@line}: '.' separator expected after major version"
        return nil
      end
      version << '.'
      skip # Skip the separator
      
      c = cur
      while ((c >= '0') && (c <= '9')) # Snagging our minor version
        version << c
        skip
        c = cur
      end
      return version
    end
    
    # xmlParseEncodingDecl
    # parse an XML encoding declaration
    #
    # [80] EncodingDecl ::= S 'encoding' Eq ('"' EncName '"' |  "'" EncName "'")
    #
    # TODO: This should set up conversion filters
    #
    # Returns the encoding value or nil
    def xmlParseEncodingDecl()
      encoding = nil
      skip_blanks
      if (cmp("encoding"))
        skip(8)
        skip_blanks
        
        raise XML_Syntax_Error, "line #{@line}: '=' expected after 'encoding'" if (cur != '=')
        skip
        skip_blanks
       
        if (cur == "\"")
          skip # Skip the '\""
          encoding = xmlParseEncName()
          raise XML_Syntax_Error, "encoding type string not closed" if (cur != "\"")
          skip
        elsif (cur == "\'")
          skip # skip the "\'"
          encoding = xmlParseEncName()
          raise XML_Syntax_Error, "encoding type string not closed" if (cur != "\'")
          skip
        else
          raise XML_Syntax_Error, "line #{@line}: encoding type string not started, expected \" or \'"
        end
        return encoding
      end
    end
    
    # xmlParseEncName
    # parse the XML encoding name
    #
    # [81] EncName ::= [A-Za-z] ([A-Za-z0-9._] | '-')*
    #
    # Returns the encoding name or nil
    def xmlParseEncName()
      encoding = ""
      
      c = cur
      
      unless ((c >= 'a') && (c <= 'z')) || ((c >= 'A') && (c <= 'Z'))
        raise XML_Syntax_Error, "line #{@line}: encoding name must begin with [a-zA-Z]"
        return nil
      end
      
      while (((c >= 'a') && (c <= 'z')) ||
    	       ((c >= 'A') && (c <= 'Z')) ||
    	       ((c >= '0') && (c <= '9')) ||
    	       (c == '.') || (c == '_') ||
    	       (c == '-')) do
    	  
    	  encoding << c
    	  skip
    	  c = cur
    	end
    	return encoding
    end
    
    # xmlParseDocument
    # parse an xml document (and build a tree)
    #
    # [1] document ::= prolog element Misc*
    #
    # [22] prolog ::= XMLDecl? Misc* (doctypedecl Misc*)?
    #
    # Returns True if passes validation, throws error otherwise
    def xmlParseDocument()
      raise XML_Document_Empty, "File content is empty" if @eof_index == 0
      
      if (cmp('<?xml') && is_blank_ch?(nxt(5)))
        xmlParseXMLDecl()
        skip_blanks
      end
      
      xmlParseMisc()
      
      if (cmp('<!DOCTYPE'))
        xmlParseDocTypeDecl()
        xmlParseInternalSubset() if cur == '['
      end
      
    end
    
    # xmlParseMisc
    # parse an XML Misc* optional field
    #
    # [27] Misc ::= Comment | PI | S
    #
    def xmlParseMisc()
      while ((cur == '<') && (nxt(1) == '?') || cmp('<!--') || is_blank?)
        if ((cur == '<') && (nxt(1) == '?'))
          xmlParsePI()
        elsif is_blank?
          skip
        else
          xmlParseComment()
        end
      end
    end
    
    # xmlParseDocTypeDecl
    # parse a DOCTYPE declaration
    #
    # [28] doctypedecl ::= '<!DOCTYPE' S Name (S ExternalID)? S? 
    #                      ('[' (markupdecl | PEReference | S)* ']' S?)? '>'
    #
    def xmlParseDocTypeDecl()
      if (cmp('<!DOCTYPE'))
        skip(9)
        skip_blanks
      
        name = xmlParseName()
        raise XML_Syntax_Error, "DOCTYPE name required!" if name.nil?
        
        skip_blanks
        uri = xmlParseExternalID()
        
        skip_blanks
        return if cur == '[' # If there are any internal subset decls it's handled external
        
        raise XML_Syntax_Error, "DOCTYPE not finished!" if (cur != '>')
        skip
      end
    end
    
    # xmlParseInternalSubset
    # parse the internal subset declaration
    #
    # [28 end] ('[' (markupdecl | PEReference | S)* ']' S?)? '>'
    #
    # TODO: xmlParsePEReference
    def xmlParseInternalSubset
      if (cur == '[')
        skip
        
        while (cur != ']')
          skip_blanks
          xmlParseMarkupDecl()
          xmlParsePEReference()
        end
        if (cur == ']')
          skip
          skip_blanks
        end
      end
      
      raise XML_Syntax_Error, "DOCTYPE not finished!" if (cur != '>')
      skip
    end
    
    # xmlParseMarkupDecl
    # parse markup declarations
    #
    # [29] markupdecl ::= elementdecl | AttlistDecl | EntityDecl |
    #                     NotationDecl | PI | Comment
    #
    # TODO: xmlParseElementDecl, xmlParseEntityDecl, xmlParseAttributeListDecl, xmlParseNotationDecl
    def xmlParseMarkupDecl
      if (cur == '<')
        if (nxt(1) == '!')
          case nxt(2)
            when 'E'
              if nxt(3) == 'L'
                xmlParseElementDecl()
              elsif nxt(3) == 'N'
                xmlParseEntityDecl()
              end
            when 'A'
              xmlParseAttributeListDecl()
            when 'N'
              xmlParseNotationDecl()
            when '-'
              xmlParseComment()
          end
        elsif (nxt(1) == '?')
          xmlParsePI()
        end
      end
    end
    
  end
  
  class DTDParser < Parser
    
    def xmlParseMarkupDecl()
      @index = 0
    end
  
    def xmlParseElementDecl()
    end
  
    def xmlParseAttributeDecl()
    end
  
    def xmlParseEntityDecl()
    end
  
    def xmlParseNotationDecl()
    end
  end
  
  class XMLParser < Parser
  end
  
end